import time
from picamera2 import Picamera2
from datetime import datetime

# Initialize camera
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (1920, 1080)})
picam2.configure(config)
picam2.start()

print("Camera started. Taking pictures every 5 seconds... (Press Ctrl+C to stop)")

try:
    while True:
        # Generate a unique filename using timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.jpg"

        # Capture and save image
        picam2.capture_file(filename)
        print(f"Saved {filename}")

        # Wait a few seconds before next shot
        time.sleep(5)  # change this value for faster/slower capture

except KeyboardInterrupt:
    print("Stopping camera...")
    picam2.stop()
