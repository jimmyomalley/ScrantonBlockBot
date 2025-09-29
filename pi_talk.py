from microbit import *

while True:
    # Button A
    if button_a.was_pressed():
        pin0.write_analog(1000)

    # Button B
    if button_b.is_pressed():
        pin14.write_analog(1000)

    # Pin1 input -> Pin16 output
    if pin1.read_digital() == 1:
        pin16.write_analog(1023)
    else:
        pin16.write_analog(0)

    # Pin0 input -> Pin12 output
    if pin0.read_digital() == 1:
        pin12.write_analog(1023)
    else:
        pin12.write_analog(0)

    # Pin14 input -> Pin8 output
    if pin14.read_digital() == 1:
        pin8.write_analog(650)
    else:
        pin8.write_analog(0)

    # Pin15 input -> Pin9 output
    if pin15.read_digital() == 1:
        pin9.write_analog(650)
    else:
        pin9.write_analog(0)
