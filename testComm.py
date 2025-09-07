import serial
import time

# Open the serial port to the Micro:bit
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

time.sleep(2)  # give the connection a moment

def send_message(message):
    # Add newline so Micro:bit's uart.readline() can detect end of command
    ser.write((message + "\n").encode("utf-8"))
    print("Sent:", message)

def receive_message():
    if ser.in_waiting > 0:
        response = ser.readline().decode("utf-8", errors="ignore").strip()
        return response
    return None

try:
    while True:
        command = input("Enter servo position (left, right, center, tcenter, tleft, tright): ")
        send_message(command)

        # wait a moment for Micro:bit to respond
        time.sleep(0.1)
        response = receive_message()
        if response:
            print("Micro:bit:", response)

        time.sleep(1)

except KeyboardInterrupt:
    print("Communication ended.")
    ser.close()
