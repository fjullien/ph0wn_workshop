#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Franck Jullien <franck.jullien@collshade.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import LiteXModule

from litex_boards.platforms import qmtech_ep4ce15_starter_kit

from litex.soc.cores.clock import CycloneIVPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from controller import SevenSegmentsController

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # # #

        # Clk / Rst
        clk50 = platform.request("clk50")

        # PLL
        self.pll = pll = CycloneIVPLL(speedgrade="-6")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=50e6,
        with_jtaguart   = False,
	with_jtagbone   = False,
        **kwargs):
        platform = qmtech_ep4ce15_starter_kit.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        if with_jtagbone:
            kwargs["uart_name"] = "crossover"
        if with_jtaguart:
            kwargs["uart_name"] = "jtag_uart"

        SoCCore.__init__(self, platform, sys_clk_freq,
            ident = "LiteX SoC on QMTECH Cyclone IV Starter Kit",
            **kwargs
        )

        # JTAGbone ---------------------------------------------------------------------------------
        if with_jtagbone:
            self.add_jtagbone()

        seven_seg = platform.request("seven_seg_ctl", 0)

        # Instance of our display controller
        self.submodules.seven_seg_ctrl = seven_seg_ctrl = SevenSegmentsController(1e9/sys_clk_freq)
        self.add_csr("seven_segment")

        # Here you must assign signals/values our controller's interfaces
        self.comb += [
            seven_seg.dig.eq(seven_seg_ctrl.digit),
            seven_seg.segments.eq(seven_seg_ctrl.abcdefg),
        ]

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=qmtech_ep4ce15_starter_kit.Platform, description="LiteX SoC on QMTECH EP4CE15")
    parser.add_target_argument("--sys-clk-freq",  default=50e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-jtaguart", action="store_true",      help="Enable JTAGUart support.")
    parser.add_target_argument("--with-jtagbone", action="store_true",      help="Enable JTAGbone support.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq           = args.sys_clk_freq,
        with_jtaguart          = args.with_jtaguart,
	with_jtagbone          = args.with_jtagbone,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
