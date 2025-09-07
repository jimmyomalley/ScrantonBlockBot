from microbit import *

uart.init(baudrate=115200)

while True:
    if uart.any():
        line = uart.readline()
        if line:
            cmd = line.decode('utf-8', 'ignore').strip().lower()
            if cmd == "left":
                display.show("L"); sleep(800); display.clear()
                uart.write("ack:left\n")
            elif cmd == "right":
                display.show("R"); sleep(800); display.clear()
                uart.write("ack:right\n")
            elif cmd == "center":
                display.show("C"); sleep(800); display.clear()
                uart.write("ack:center\n")
            else:
                display.show("?"); sleep(500); display.clear()
                uart.write("err:unknown\n")
    sleep(10)
