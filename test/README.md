# Testbench for Shiftregister Challenge 40 Bit

This testbench uses [cocotb](https://docs.cocotb.org/en/stable/) to verify the 40-bit shift register challenge design.

## Setting up

1. Ensure `PROJECT_SOURCES` in [Makefile](Makefile) points to `../src/project.v` (already set).
2. Ensure `tb.v` instantiates `tt_um_thorsten_shiftregister` (already set).

## How to run

RTL simulation:

```sh
make -B
```

Gate-level simulation (after hardening):

```sh
cp ../runs/wokwi/results/final/verilog/gl/tt_um_thorsten_shiftregister.v gate_level_netlist.v
make -B GATES=yes
```

## View waveforms

```sh
# GTKWave
gtkwave tb.fst tb.gtkw

# Surfer
surfer tb.fst
```

## Test cases

| Test | Description |
|------|-------------|
| `test_reset_output_low` | Output is 0 directly after reset |
| `test_wrong_key_output_low` | Shifting a wrong 40-bit value keeps output low |
| `test_correct_key_output_high` | Shifting the correct secret key raises output to 1 |
| `test_one_more_bit_clears_output` | One extra shift after the key drops the output back to 0 |
| `test_shift_enable_inactive` | Shift enable = 0 prevents register updates |
| `test_sliding_window` | Output pulses exactly once at the correct 40-bit alignment |
