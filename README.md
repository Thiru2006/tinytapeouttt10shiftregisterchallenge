![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg) ![](../../workflows/fpga/badge.svg)

# Shiftregister Challenge 40 Bit

**Author:** Thorsten Knoll

A 40-bit shift register challenge implemented for [Tiny Tapeout](https://tinytapeout.com).

- [Read the project documentation](docs/info.md)

## What does it do?

The design contains a 40-bit shift register with a **secret hardcoded 40-bit number** inside. Your challenge: find the correct 40-bit sequence to make the output go HIGH. Every other combination of 40 bits will keep the output LOW.

There are **2^40 ≈ 1 trillion** possible combinations. Good luck! 🔐

## Pinout

| Pin | Direction | Function |
|-----|-----------|----------|
| `ui[0]` | Input | Serial data input |
| `ui[1]` | Input | Shift enable (active high) |
| `uo[0]` | Output | **HIGH when correct key is found** |
| `clk` | Input | Clock |
| `rst_n` | Input | Active-low reset |

## How to use

1. Reset the design (`rst_n` low, then high).
2. Assert `ui[1]` (shift enable) high.
3. Clock in your 40-bit candidate on `ui[0]`, **MSB first**, one bit per clock cycle.
4. After 40 cycles, check `uo[0]`.

The register is a sliding window — you can keep clocking to check new candidates continuously.

## What is Tiny Tapeout?

Tiny Tapeout is an educational project that makes it easier and cheaper than ever to get your digital designs manufactured on a real chip. Visit [tinytapeout.com](https://tinytapeout.com) to learn more.

## Resources

- [FAQ](https://tinytapeout.com/faq/)
- [Digital design lessons](https://tinytapeout.com/digital_design/)
- [Join the community](https://tinytapeout.com/discord)
