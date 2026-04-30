/*
 * Copyright (c) 2024 Thorsten Knoll
 * SPDX-License-Identifier: Apache-2.0
 *
 * 40-Bit Shift Register Challenge
 *
 * Description:
 *   A 40-bit shift register with a hardcoded secret 40-bit number.
 *   The challenge is to find the correct 40-bit sequence to enable
 *   the output high. With all other input sequences the output is low.
 *
 * How to use:
 *   - Use ui_in[0] as serial data input (shift in data bit by bit)
 *   - Use ui_in[1] as shift enable (active high)
 *   - Clock in 40 bits serially
 *   - uo_out[0] goes HIGH only when the correct 40-bit sequence is present
 *   - uo_out[1..7] are always 0
 *   - rst_n (active low) resets the shift register to all zeros
 */

`default_nettype none

module tt_um_thorsten_shiftregister (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // Secret 40-bit key (that's for us to know and you to find out!)
  localparam [39:0] SECRET_KEY = 40'hA5_3C_96_6F_B2;

  // 40-bit shift register
  reg [39:0] shift_reg;

  // Serial data input: ui_in[0]
  // Shift enable:      ui_in[1]
  wire serial_in  = ui_in[0];
  wire shift_en   = ui_in[1];

  // Shift register logic: shift left, new bit enters at LSB
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      shift_reg <= 40'b0;
    end else if (shift_en) begin
      shift_reg <= {shift_reg[38:0], serial_in};
    end
  end

  // Output: HIGH only when shift register matches the secret key
  assign uo_out[0] = (shift_reg == SECRET_KEY) ? 1'b1 : 1'b0;
  assign uo_out[7:1] = 7'b0;

  // Bidirectional IOs not used
  assign uio_out = 8'b0;
  assign uio_oe  = 8'b0;

  // Suppress unused input warnings
  wire _unused = &{ena, uio_in, ui_in[7:2], 1'b0};

endmodule
