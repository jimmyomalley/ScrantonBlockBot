import serial
import time

# open the serial port to the Micro:bit
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
time.sleep(2)  # allow time to connect

def send_message(message):
    # add newline so Micro:bit's uart.readline() can detect end of command
    ser.write((message + "\n").encode("utf-8"))
    print("Sent:", message)

def receive_message():
    if ser.in_waiting > 0:
        return ser.readline().decode("utf-8", errors="ignore").strip()
    return None

try:
    while True:
        command = input("Enter command (left, right, center): ").strip()
        if not command:
            continue
        send_message(command)

        # wait a bit for Micro:bit to reply
        time.sleep(0.1)
        response = receive_message()
        if response:
            print("Micro:bit:", response)

except KeyboardInterrupt:
    print("Communication ended.")
    ser.close()

