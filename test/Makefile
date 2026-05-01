# SPDX-FileCopyrightText: © 2024 Thorsten Knoll
# SPDX-License-Identifier: Apache-2.0

SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# RTL source
PROJECT_SOURCES = ../src/project.v

ifneq ($(GATES),yes)

# RTL simulation
VERILOG_SOURCES += $(PWD)/tb.v
VERILOG_SOURCES += $(PROJECT_SOURCES)

else

# Gate-level simulation
# FUNCTIONAL removes power pins (VPWR/VGND/VNB/VPB) from cell models
# UNIT_DELAY gives simple timing for simulation
COMPILE_ARGS    += -DGL_TEST
COMPILE_ARGS    += -DFUNCTIONAL
COMPILE_ARGS    += -DUNIT_DELAY="#1"
COMPILE_ARGS    += -I $(PDK_ROOT)/$(PDK)/libs.ref/sky130_fd_sc_hd/verilog
VERILOG_SOURCES += $(PDK_ROOT)/$(PDK)/libs.ref/sky130_fd_sc_hd/verilog/primitives.v
VERILOG_SOURCES += $(PDK_ROOT)/$(PDK)/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v
VERILOG_SOURCES += $(PWD)/gate_level_netlist.v
VERILOG_SOURCES += $(PWD)/tb.v

endif

TOPLEVEL = tb
MODULE   = test

include $(shell cocotb-config --makefiles)/Makefile.sim
