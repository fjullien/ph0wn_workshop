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

        # "0" -> ABCDEFG = 0b1000000
        # "1" -> ABCDEFG = 0b1111001
        # "2" -> ABCDEFG = 0b0100100
        # "3" -> ABCDEFG = 0b0110000
        # "4" -> ABCDEFG = 0b0011001
        # "5" -> ABCDEFG = 0b0010010
        # "6" -> ABCDEFG = 0b0000010
        # "7" -> ABCDEFG = 0b1111000
        # "8" -> ABCDEFG = 0b0000000
        # "9" -> ABCDEFG = 0b0010000
        # "A" -> ABCDEFG = 0b0001000
        # "b" -> ABCDEFG = 0b0000011
        # "c" -> ABCDEFG = 0b1000110
        # "d" -> ABCDEFG = 0b0100001
        # "E" -> ABCDEFG = 0b0000110
        # "F" -> ABCDEFG = 0b0001110

        # You can use If/Else or Case

        # Case/Switch statement

        # Parameters
        # ----------
        # test : _Value, in
        #     Selector value used to decide which block to execute
        # cases : dict
        #     Dictionary of cases. The keys are numeric constants to compare
        #     with `test`. The values are statements to be executed the
        #     corresponding key matches `test`. The dictionary may contain a
        #     string key `"default"` to mark a fall-through case that is
        #     executed if no other key matches.

        # Examples
        # --------
        # >>> a = Signal()
        # >>> b = Signal()
        # >>> Case(a, {
        # ...     0:         b.eq(1),
        # ...     1:         b.eq(0),
        # ...     "default": b.eq(0),
        # ... })

        # Don't forget to place your logic in a sync or comb section

        # Combinatorial assignement
        # ...

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
                # Each time count is equal to refresh_count, we need to assign
                # digit a new value

                #......

            )
        ]

        #----------------------------------------------------------------------------
        #- Choose the value applied to segments
        #----------------------------------------------------------------------------
        segments_value = Signal(4)

        # Depending on the value of digit, the corresponding par of signal value (here segments_value)
        # must be selected. It will be connected to the SevenSegment's input

        # ...

        #----------------------------------------------------------------------------
        #- Use the SevenSegment module and connect it to our signals
        #----------------------------------------------------------------------------

        #....

        self.comb += [
            #....
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
            #...
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
