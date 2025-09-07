import serial
import time

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

time.sleep(2)

def send_message(message):
    ser.write(message.encode('utf-8'))
    print(f"Sent: {message}")
    
def receive_message():
    if ser.in_waiting >0:
        response =ser.readline().decode('utf-8').strip()
        return response
    return None
    
try:
    while True:
        command = input("Enter servo position (left, right, center, tcenter, tleft, tright): ")
        send_message(command)
        time.sleep(1)
        
except KeyboardInterrupt:
    print("Communcation ended.")
finally:
    ser.close()
