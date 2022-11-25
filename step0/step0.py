#!/usr/bin/env python3

import sys
import os

from migen import *
from litex.build.io import CRG
from litex_boards.platforms import qmtech_ep4ce15_starter_kit

# Blinker -------------------------------------------------------------------------------------------


class Blink(Module):
    def __init__(self, bit):
        # This signal, declared as a attribute of the class
        # can be accessed from outside the module.
        self.out = Signal()

        ###

        # Internal signal
        counter = Signal(25)

        # This is the actual counter. It is incremented each clock cycle.
        # Because it's not just only wires, it needs some memory (registers)
        # it has to be in a synchronous block.
        self.sync += counter.eq(counter + 1)

        # Combinatorial assignments can be seen as wires.
        # Here we connect a bit of the counter to the self.out signal
        self.comb += self.out.eq(counter[bit])

# Design -------------------------------------------------------------------------------------------

class Tuto(Module):
    def __init__(self, platform):

        # Get pin from ressources
        clk = platform.request("clk50")
        led0 = platform.request("led", 0)

        # Creates a "sys" clock domain and generates a startup reset
        crg = CRG(clk)
        self.submodules.crg = crg

        # Instance of Blink
        blink = Blink(22)
        self.submodules += blink
        self.comb += led0.eq(blink.out)

# Test -------------------------------------------------------------------------------------------

def bench():
    loop = 0
    while (loop < 10000):
        yield
        loop = loop + 1

def main():

    # Instance of our platform (which is in litex_boards.platforms)
    platform = qmtech_ep4ce15_starter_kit.Platform()
    design = Tuto(platform)

    if "load" in sys.argv[1:]:
        prog = platform.create_programmer()
        prog.load_bitstream(os.path.join("gateware", "top.sof"))
        exit()

    if "sim" in sys.argv[1:]:
        blink = Blink(3)
        run_simulation(blink, bench(), vcd_name="sim.vcd")
        exit()

    platform.build(design, build_dir="gateware")

if __name__ == "__main__":
    main()
