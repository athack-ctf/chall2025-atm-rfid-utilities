from escpos import *

p = printer.Usb(0x0416,0x5011, profile='POS-5890', in_ep=0x81, out_ep=0x03)

# Print text
p.text("ATHACKCTF{Hehehehehehehe}\n")