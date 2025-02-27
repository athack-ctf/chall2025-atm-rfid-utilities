from escpos import *


def print_and_exit(p):
    # INSTEAD; print some stuff for next one (it's in the railee)
    for i in range(37):
        p.text("\n")



p = printer.Usb(0x0416,0x5011, profile='POS-5890', in_ep=0x81, out_ep=0x03)


p.text("ATHACKCTF{}\n")

print_and_exit(p)
