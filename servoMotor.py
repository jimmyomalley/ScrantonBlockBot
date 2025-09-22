# --- Configurable inputs (you can overwrite these from radio/serial/buttons) ---
command = "sm"  # "sm" (servo) | "dc" (PWM DC) | "dd" (digital DC)
data1 = 0       # left motor/servo control
data2 = 0       # right motor/servo control


# Helper: clamp a value into [lo, hi]
def clamp(v, lo, hi):
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


# Helper: write PWM safely (0..1023)
def write_pwm(pin, value):
    pins.analog_write_pin(pin, clamp(value, 0, 1023))


# Main loop
def on_forever():
    # Read the globals (replace these with your own input sources later)
    # command, data1, data2 are already globals; no assignment here so no 'global' needed

    if command == "sm":
        # SERVO mode:
        # data1 = which servo (1->P13, 2->P14, 3->P15)
        # data2 = angle (0..180)
        angle = clamp(data2, 0, 180)
        if data1 == 1:
            pins.servo_write_pin(AnalogPin.P13, angle)
        elif data1 == 2:
            pins.servo_write_pin(AnalogPin.P14, angle)
        elif data1 == 3:
            pins.servo_write_pin(AnalogPin.P15, angle)
        else:
            # no valid servo selected; do nothing
            pass

    elif command == "dc":
        # DC MOTOR PWM mode:
        # Left motor uses P8/P9, Right motor uses P12/P16
        # Positive = forward on the second pin in each pair

        # Left motor (P8, P9)
        if data1 > 0:
            write_pwm(AnalogPin.P9, abs(data1))
            write_pwm(AnalogPin.P8, 0)
        elif data1 < 0:
            write_pwm(AnalogPin.P8, abs(data1))
            write_pwm(AnalogPin.P9, 0)
        else:
            write_pwm(AnalogPin.P8, 0)
            write_pwm(AnalogPin.P9, 0)

        # Right motor (P12, P16)
        if data2 > 0:
            write_pwm(AnalogPin.P16, abs(data2))
            write_pwm(AnalogPin.P12, 0)
        elif data2 < 0:
            write_pwm(AnalogPin.P12, abs(data2))
            write_pwm(AnalogPin.P16, 0)
        else:
            write_pwm(AnalogPin.P12, 0)
            write_pwm(AnalogPin.P16, 0)

    elif command == "dd":
        # DC MOTOR DIGITAL mode (full on/off only):

        # Left motor on P8/P9
        if data1 > 0:
            pins.digital_write_pin(DigitalPin.P9, 1)
            pins.digital_write_pin(DigitalPin.P8, 0)
        elif data1 < 0:
            pins.digital_write_pin(DigitalPin.P8, 1)
            pins.digital_write_pin(DigitalPin.P9, 0)
        else:
            pins.digital_write_pin(DigitalPin.P8, 0)
            pins.digital_write_pin(DigitalPin.P9, 0)

        # Right motor on P12/P16
        if data2 > 0:
            pins.digital_write_pin(DigitalPin.P16, 1)
            pins.digital_write_pin(DigitalPin.P12, 0)
        elif data2 < 0:
            pins.digital_write_pin(DigitalPin.P12, 1)
            pins.digital_write_pin(DigitalPin.P16, 0)
        else:
            pins.digital_write_pin(DigitalPin.P12, 0)
            pins.digital_write_pin(DigitalPin.P16, 0)

    # Small delay to avoid saturating the CPU/PWM hardware
    basic.pause(10)


basic.forever(on_forever)
