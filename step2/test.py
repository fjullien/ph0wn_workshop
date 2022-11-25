#!/usr/bin/env python3

import sys
import time

from litex import RemoteClient

wb = RemoteClient()
wb.open()

# # #

mems = [x for x in dir(wb.mems) if not x.startswith("__")]
print(mems)

mems = [x for x in dir(wb.mems.csr) if not x.startswith("__")]
print(mems)

# Access the WB bus
wb.write(wb.mems.csr.base + 0x1800, 0x101)

time.sleep(5)

# Access a specific register
for i in range(20):
	wb.regs.seven_seg_ctrl_value.write(i)


# # #

wb.close()