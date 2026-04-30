# SPDX-FileCopyrightText: © 2024 Thorsten Knoll
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

# The secret 40-bit key — must match the localparam SECRET_KEY in project.v
SECRET_KEY = 0xA5_3C_96_6F_B2
KEY_BITS   = 40


async def reset_dut(dut):
    """Hold reset for 5 cycles then release."""
    dut.ena.value    = 1
    dut.ui_in.value  = 0
    dut.uio_in.value = 0
    dut.rst_n.value  = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value  = 1
    await ClockCycles(dut.clk, 2)


async def shift_in_value(dut, value, nbits=KEY_BITS):
    """
    Shift 'nbits' bits of 'value' MSB-first into the DUT.
    ui_in[1] = shift_en = 1, ui_in[0] = serial data bit.
    After the last bit, we wait one more rising edge with shift_en=0
    so the output is stable before we read it.
    """
    for i in range(nbits - 1, -1, -1):
        bit = (value >> i) & 1
        dut.ui_in.value = (1 << 1) | bit   # shift_en=1, serial_in=bit
        await RisingEdge(dut.clk)

    # Deassert shift_en and let output settle for one cycle
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 1)


def output_bit(dut):
    """Return the integer value of uo_out[0] (the challenge output pin)."""
    return int(dut.uo_out.value) & 0x01


# ---------------------------------------------------------------------------
# Test 1: After reset the output must be low
# ---------------------------------------------------------------------------
@cocotb.test()
async def test_reset_output_low(dut):
    """After reset the output must be low (shift register is all zeros)."""
    dut._log.info("Test 1: output is low after reset")
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    await reset_dut(dut)
    assert output_bit(dut) == 0, "uo_out[0] should be 0 right after reset"


# ---------------------------------------------------------------------------
# Test 2: All-zeros key does not match
# ---------------------------------------------------------------------------
@cocotb.test()
async def test_all_zeros_output_low(dut):
    """Shifting 40 zeros must keep output low."""
    dut._log.info("Test 2: all-zeros sequence keeps output low")
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    await reset_dut(dut)
    await shift_in_value(dut, 0x00_00_00_00_00)
    assert output_bit(dut) == 0, "uo_out[0] should be 0 for all-zeros input"


# ---------------------------------------------------------------------------
# Test 3: All-ones key does not match
# ---------------------------------------------------------------------------
@cocotb.test()
async def test_all_ones_output_low(dut):
    """Shifting 40 ones must keep output low."""
    dut._log.info("Test 3: all-ones sequence keeps output low")
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    await reset_dut(dut)
    await shift_in_value(dut, 0xFF_FF_FF_FF_FF)
    assert output_bit(dut) == 0, "uo_out[0] should be 0 for all-ones input"


# ---------------------------------------------------------------------------
# Test 4: Correct secret key raises output
# ---------------------------------------------------------------------------
@cocotb.test()
async def test_correct_key_output_high(dut):
    """Shifting in the correct 40-bit secret key must raise uo_out[0]."""
    dut._log.info("Test 4: correct key raises output high")
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    await reset_dut(dut)
    await shift_in_value(dut, SECRET_KEY)
    assert output_bit(dut) == 1, (
        f"uo_out[0] should be 1 after shifting correct key 0x{SECRET_KEY:010X}, "
        f"got {output_bit(dut)}"
    )


# ---------------------------------------------------------------------------
# Test 5: One extra bit after the key clears the output
# ---------------------------------------------------------------------------
@cocotb.test()
async def test_extra_bit_clears_output(dut):
    """After the correct key, one extra shift must clear uo_out[0]."""
    dut._log.info("Test 5: extra bit after correct key clears output")
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    await reset_dut(dut)
    await shift_in_value(dut, SECRET_KEY)
    assert output_bit(dut) == 1, "Precondition: output should be 1 after correct key"

    # Shift in one more 0 bit with shift_en=1, then settle
    dut.ui_in.value = (1 << 1) | 0   # shift_en=1, serial_in=0
    await RisingEdge(dut.clk)
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 1)
    assert output_bit(dut) == 0, "uo_out[0] must go back to 0 after one extra shift"


# ---------------------------------------------------------------------------
# Test 6: shift_en = 0 prevents the register from updating
# ---------------------------------------------------------------------------
@cocotb.test()
async def test_shift_enable_gating(dut):
    """With shift_en=0, clocking data in must never change the register."""
    dut._log.info("Test 6: shift_en=0 gates all updates")
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    await reset_dut(dut)

    # Attempt to shift the correct key in with shift_en=0
    for i in range(KEY_BITS - 1, -1, -1):
        bit = (SECRET_KEY >> i) & 1
        dut.ui_in.value = (0 << 1) | bit   # shift_en=0
        await RisingEdge(dut.clk)

    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 1)

    assert output_bit(dut) == 0, (
        "uo_out[0] must remain 0 when shift_en=0 — register must not have changed"
    )


# ---------------------------------------------------------------------------
# Test 7: Sliding window — output pulses exactly once in an 80-bit stream
# ---------------------------------------------------------------------------
@cocotb.test()
async def test_sliding_window(dut):
    """
    Stream 80 bits: 40 zeros followed by the secret key.
    Output must be LOW during the 40 zeros, HIGH after the key is loaded,
    then LOW again after one more bit is clocked in.
    """
    dut._log.info("Test 7: sliding window — output pulses exactly once")
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    await reset_dut(dut)

    # Phase 1: 40 zeros — register stays all-zero, output stays LOW
    await shift_in_value(dut, 0x00_00_00_00_00, nbits=40)
    assert output_bit(dut) == 0, "Output must be LOW after 40 zeros"

    # Phase 2: shift the secret key MSB-first — output goes HIGH
    await shift_in_value(dut, SECRET_KEY, nbits=40)
    assert output_bit(dut) == 1, "Output must be HIGH after correct key is fully loaded"

    # Phase 3: one more bit with shift_en=1 — register slides past the key
    dut.ui_in.value = (1 << 1) | 0
    await RisingEdge(dut.clk)
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 1)
    assert output_bit(dut) == 0, "Output must drop back to LOW after sliding past the key"


# ---------------------------------------------------------------------------
# Test 8: Reset clears a loaded key
# ---------------------------------------------------------------------------
@cocotb.test()
async def test_reset_clears_key(dut):
    """Asserting reset after the key is loaded must immediately clear output."""
    dut._log.info("Test 8: reset clears a previously loaded key")
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    await reset_dut(dut)
    await shift_in_value(dut, SECRET_KEY)
    assert output_bit(dut) == 1, "Precondition: key should be loaded"

    # Assert reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    assert output_bit(dut) == 0, "uo_out[0] must be 0 while rst_n is asserted"

    # Release reset
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    assert output_bit(dut) == 0, "uo_out[0] must remain 0 after reset is released"
