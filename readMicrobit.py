import serial   # Library for talking to devices over serial (USB)
import time     # Library for delays and timing

# Replace with your actual serial port
#   Windows → "COM3", "COM4", etc.
#   Linux/Mac → "/dev/ttyACM0" or "/dev/ttyUSB0"
PORT = "/dev/ttyACM0"   
BAUD_RATE = 115200      # Must match the baud rate used by the micro:bit

try:
    # Open the serial connection to the micro:bit
    ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {PORT} at {BAUD_RATE} baud.")

    while True:  # Infinite loop to keep reading data
        if ser.in_waiting > 0:  # Check if any bytes have arrived
            line = ser.readline().decode('utf-8').strip()  
            # Read one line from the serial, decode from bytes to string, remove \n
            print(f"Received from micro:bit: {line}")  
        time.sleep(0.1)  # Small pause so the loop doesn’t hog the CPU

except serial.SerialException as e:
    # This block runs if opening/using the serial port fails
    print(f"Error: {e}")

finally:
    # Always close the port when the program ends
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port closed.")
