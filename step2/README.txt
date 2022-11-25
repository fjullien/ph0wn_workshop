#----------------------------------------------------
#-
#----------------------------------------------------

./step2.py --build --with-jtaguart --load --csr-csv csr.csv

litex_term jtag --jtag-config ./openocd_cyclone4_blaster.cfg

ident
mem_write 0xf0001800 0x123

#----------------------------------------------------
#-
#----------------------------------------------------

./step2_bis.py --build --with-jtagbone --load --csr-csv csr.csv

In one terminal:
--------------------
litex_server --jtag --jtag-config ./openocd_cyclone4_blaster.cfg

In another terminal:
---------------------

litex_cli --regs
litex_cli --write 0xf0001800 0x123

sudo -H pip3 install dearpygui
litex_cli --gui

./test.py


