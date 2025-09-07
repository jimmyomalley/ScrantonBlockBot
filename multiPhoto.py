import time
import string
import random
from picamera2 import Picamera2
from PIL import Image

# Function to generate a random 4-character string
def random_filename(length=4):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

picam2 = Picamera2()
camera_config = picam2.create_still_configuration(main={"size": (1920,1080)})
picam2.configure(camera_config)
picam2.start()
time.sleep(2)

# Generate random filename
filename = random_filename() + ".jpg"

# Capture and save the image
picam2.capture_file(filename)
print(f"Image saved as {filename}")

image_array = picam2.capture_array()
picam2.stop()


