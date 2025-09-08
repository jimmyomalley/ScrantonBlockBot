from microbit import *   # Import all micro:bit-specific modules

while True:  # Infinite loop so the program keeps running
    x = accelerometer.get_x()          # Read the accelerometer value on the X-axis
    display.scroll(str(x))             # Show the value on the micro:bit LED display
    uart.write(str(x) + '\n')          # Send the value over the serial (USB) with newline
    sleep(1000)                        # Wait 1000 ms (1 second) before repeating
