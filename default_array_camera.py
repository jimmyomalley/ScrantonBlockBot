from picamera2 import Picamera2
from PIL import Image
import numpy as np
import time

def pbox(ia,x,y,d):
    ix=int(x-(d/2))
    iy=int(y-(d/2))
    # top and bottom line
    for i in range(ix,x+d):
        ia[iy,i]=[0,0,0]
        ia[y+d,i]=[0,0,0]
    for j in range(iy,y+d):
        ia[j,ix]=[0,0,0]
        ia[j,x+d]=[0,0,0]
       
    return ia

# Create a Picamera2 object
picam2 = Picamera2()

    # Configure the camera for a preview and capture
    # You can adjust the resolution as needed
camera_config = picam2.create_still_configuration(main={"size": (1920, 1080)})
                                                                 
picam2.configure(camera_config)

    # Start the camera (and optionally a preview)
    # If you want a preview window, uncomment the line below:
    # from picamera2 import Preview
    # picam2.start_preview(Preview.QTGL)
picam2.start()

    # Wait for the camera to initialize (adjust as needed)
time.sleep(2)

    # Capture the image and save it
picam2.capture_file("blocks.jpg")

image_array = picam2.capture_array()

    # Stop the camera
picam2.stop()

print("Picture taken and saved as blocks.jpg")

print(f"caputred image array shape:{image_array.shape}")
a,b=200,200
c,d=50,90
for i in range (0,d):
    # print(image_array[i,200])
    for j in range (0,c):
        image_array[i+a,j+b]=[0,0,0]
        image_array[i+a,j+b+c]=[255,0,0] 
        image_array[i+a,j+b+2*c]=[0,255,0]
        image_array[i+a,j+b+3*c]=[0,0,255]
        image_array[i+a,j+b+4*c]=[255,255,0]

image_array=pbox(image_array,400,800,100)

    
img=Image.fromarray(image_array)
img.save("my_picture3b.jpg")

print("modified picture saved as my_picture3b")
