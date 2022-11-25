#!/usr/bin/env python3

import sys
import os

from migen import *
from litex.build.io import CRG
from litex_boards.platforms import qmtech_ep4ce15_starter_kit

# Blinker -------------------------------------------------------------------------------------------

class SevenSegment(Module):
    def __init__(self):
        self.value   = value   = Signal(4)     # input
        self.abcdefg = abcdefg = Signal(7)     # output

        # # #

        # If(value == 0,
        #     abcdefg.eq(0b0111111)
        # ).Elif(value == 1,
        #     abcdefg.eq(0b0111111)
        # ...

        #----------------------------------------------------------------------------
        #- Value to abcd segments dictionary.
        #- Here we create a table to translate each of the 16 possible input
        #- values to abdcefg segments control.
        #----------------------------------------------------------------------------
        cases = {
          0x0: abcdefg.eq(0b1000000),
          0x1: abcdefg.eq(0b1111001),
          0x2: abcdefg.eq(0b0100100),
          0x3: abcdefg.eq(0b0110000),
          0x4: abcdefg.eq(0b0011001),
          0x5: abcdefg.eq(0b0010010),
          0x6: abcdefg.eq(0b0000010),
          0x7: abcdefg.eq(0b1111000),
          0x8: abcdefg.eq(0b0000000),
          0x9: abcdefg.eq(0b0010000),
          0xa: abcdefg.eq(0b0001000),
          0xb: abcdefg.eq(0b0000011),
          0xc: abcdefg.eq(0b1000110),
          0xd: abcdefg.eq(0b0100001),
          0xe: abcdefg.eq(0b0000110),
          0xf: abcdefg.eq(0b0001110),
        }

        # Combinatorial assignement
        self.comb += Case(value, cases)

class SevenSegmentsController(Module):
    def __init__(self, period_ns):
        self.digit   = digit   = Signal(3, reset = 1)
        self.value   = value   = Signal(12)
        self.abcdefg = abcdefg = Signal(7)

        ###

        #----------------------------------------------------------------------------
        #- Compute how many clock pulse we have to wait to get refresh_time in ms.
        #- This is pure Python, not used during verilog generation
        #----------------------------------------------------------------------------
        refresh_time  = 2 # 2 ms
        refresh_count = int(((refresh_time * 1e6) / period_ns))

        print(f"Clock frequency = {int(1e9/period_ns)}Hz")
        print(f"Need {refresh_count} clocks period to wait for {refresh_time} ms")

        #----------------------------------------------------------------------------
        #- Here we generate the signals driving anodes
        #----------------------------------------------------------------------------

        #              ┌─────────┐                    ┌─────────┐
        #  digit[0]    │         │                    │         │
        #           ───┘         └────────────────────┘         └─

        #                         ┌─────────┐
        #  digit[1]               │         │
        #           ──────────────┘         └─────────────────────

        #                                   ┌─────────┐
        #  digit[2]                         │         │
        #           ────────────────────────┘         └───────────

        count = Signal(32)

        self.sync += [
            count.eq(count + 1),
            If (count == refresh_count,
                count.eq(0),
                #----------------------------------------------------------------------------
                #- Cat() is used to concatenate several Signal()
                #- Arguments are lower values first
                #-
                #- MSB -------------------+
                #- LSB ---------+         |
                #               │         │
                #               ▼         ▼
                digit.eq(Cat(digit[2], digit[0:2]))
            )
        ]

        #----------------------------------------------------------------------------
        #- Choose the value applied to segments
        #----------------------------------------------------------------------------
        segments_value = Signal(4)

        # self.comb += [
        #     If (digit[2],
        #         segments_value.eq(value[0:4]),
        #     ),
        #     If (digit[1],
        #         segments_value.eq(value[4:8])
        #     ),
        #     If (digit[0],
        #         segments_value.eq(value[8:12])
        #     ),
        # ]

        cases = {
            0x4: segments_value.eq(value[0:4]),
            0x2: segments_value.eq(value[4:8]),
            0x1: segments_value.eq(value[8:12])
        }
        self.comb += Case(digit, cases)

        #----------------------------------------------------------------------------
        #- Use the SevenSegment module and connect it to our signals
        #----------------------------------------------------------------------------
        self.submodules.sevensegment = segments = SevenSegment()

        self.comb += [
            segments.value.eq(segments_value),
            abcdefg.eq(segments.abcdefg),
        ]

# Design -------------------------------------------------------------------------------------------

class Step1(Module):
    def __init__(self, platform):

        # Get pin from ressources
        clk = platform.request("clk50")

        # Look at the platform file (in litex_boards/platforms/) to see what are
        # the signals in the "sevent_seg_ctl" Record (a strcture of Signals)
        # You can access Signals composign a Record with ".", like in a software structure
        seven_seg = platform.request("seven_seg_ctl", 0)

        # Creates a "sys" clock domain and generates a startup reset
        crg = CRG(clk)
        self.submodules.crg = crg

        # Instance of our display controller
        self.submodules.controller = controller = SevenSegmentsController(platform.default_clk_period)

        # Here you must assign signals/values our controller's interfaces
        self.comb += [
            seven_seg.dig.eq(controller.digit),
            controller.value.eq(0xabc),
            seven_seg.segments.eq(controller.abcdefg),
        ]

# Test -------------------------------------------------------------------------------------------

def bench(dut):
    loop = 0
    # This is how we access signals from the simulation -> "yield"
    yield dut.value.eq(0x123)
    while (loop < 10000):
        yield
        loop = loop + 1

def main():

    if "sim" in sys.argv[1:]:
        # Gives a slower clock period to facilitate simulation
        dut = SevenSegmentsController(10e3)
        run_simulation(dut, bench(dut), vcd_name="sim.vcd")
        exit()

    # Instance of our platform (which is in litex_boards.platforms)
    platform = qmtech_ep4ce15_starter_kit.Platform()
    design = Step1(platform)

    if "load" in sys.argv[1:]:
        prog = platform.create_programmer()
        prog.load_bitstream(os.path.join("gateware", "top.sof"))
        exit()

    platform.build(design, build_dir="gateware")

if __name__ == "__main__":
    main()
