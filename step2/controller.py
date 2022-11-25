from migen import *

from litex.soc.interconnect.csr import AutoCSR, CSRStorage

class SevenSegment(Module):
    def __init__(self):
        self.value   = value   = Signal(4)
        self.abcdefg = abcdefg = Signal(7)

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

        self.comb += Case(value, cases)

#----------------------------------------------------------------
#-
#- Inherit from AutoCSR
#-
#----------------------------------------------------------------
class SevenSegmentsController(Module, AutoCSR):
    def __init__(self, period_ns):
        self.digit   = digit   = Signal(3, reset = 1)
        self.abcdefg = abcdefg = Signal(7)

        #----------------------------------------------------------------
        #-
        #- Declare a CSR register, writable
        #-
        #----------------------------------------------------------------
        self.value   = value   = CSRStorage(12)

        ###

        refresh_time  = 2
        refresh_count = int(((refresh_time * 1e6) / period_ns))

        count = Signal(32)

        self.sync += [
            count.eq(count + 1),
            If (count == refresh_count,
                count.eq(0),
                digit.eq(Cat(digit[2], digit[0:2]))
            )
        ]

        segments_value = Signal(4)

        #----------------------------------------------------------------
        #-
        #- Use the CSR value. !!! Use value.storage !!!
        #-
        #----------------------------------------------------------------
        cases = {
            0x4: segments_value.eq(value.storage[0:4]),
            0x2: segments_value.eq(value.storage[4:8]),
            0x1: segments_value.eq(value.storage[8:12])
        }
        self.comb += Case(digit, cases)

        self.submodules.sevensegment = segments = SevenSegment()

        self.comb += [
            segments.value.eq(segments_value),
            abcdefg.eq(segments.abcdefg),
        ]