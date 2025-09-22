import time
from datetime import datetime
from picamera2 import Picamera2
from PIL import Image
import numpy as np

# ------------------ Image Processing Helpers ------------------
def pbox(ia, ANx, ANy):
    ix, fx = ANx
    iy, fy = ANy
    # top and bottom line
    for i in range(ix, fx):
        ia[iy, i] = [0, 0, 0]
        ia[fy, i] = [0, 0, 0]
    for j in range(iy, fy):
        ia[j, ix] = [0, 0, 0]
        ia[j, fx] = [0, 0, 0]
    return ia

def cbox(ia, ANx, ANy):
    ix, fx = ANx
    iy, fy = ANy
    Amin, Amax, Bmin, Bmax, Cmin, Cmax = 255, 0, 255, 0, 255, 0
    for i in range(ix, fx):
        for j in range(iy, fy):
            A, B, C = ia[j, i, 0], ia[j, i, 1], ia[j, i, 2]
            Amin, Amax = min(Amin, A), max(Amax, A)
            Bmin, Bmax = min(Bmin, B), max(Bmax, B)
            Cmin, Cmax = min(Cmin, C), max(Cmax, C)
    return Amin, Amax, Bmin, Bmax, Cmin, Cmax

def rbox(ia, Xmax, Ymax, Amin, Amax, Bmin, Bmax, Cmin, Cmax):
    for i in range(Ymax):
        for j in range(Xmax):
            A, B, C = ia[j, i, 0], ia[j, i, 1], ia[j, i, 2]
            if Amin <= A <= Amax and Bmin <= B <= Bmax and Cmin <= C <= Cmax:
                ia[j, i] = [0, 0, 0]
    return ia

# ------------------ Camera Setup ------------------
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (1920, 1080)})
picam2.configure(config)
picam2.start()

print("Camera started. Capturing and processing every 5 seconds... (Press Ctrl+C to stop)")

# ------------------ Main Loop ------------------
try:
    while True:
        # Capture unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.jpg"
        
        # Take photo
        picam2.capture_file(filename)
        print(f"Saved {filename}")

        # Open with PIL
        img = Image.open(filename).rotate(180)  # Rotate if needed
        Xmax, Ymax = img.size[1], img.size[0]   # note swapped axes
        img_array = np.array(img)

        # Define analysis box
        ANx = [1180, 1730]  # adjust as needed
        ANy = [50, 250]

        # Add reference color blocks
        a, b, c, d = 200, 200, 50, 90
        for i in range(0, d):
            for j in range(0, c):
                img_array[i+a, j+b]     = [0, 0, 0]
                img_array[i+a, j+b+c]   = [255, 0, 0]
                img_array[i+a, j+b+2*c] = [0, 255, 0]
                img_array[i+a, j+b+3*c] = [0, 0, 255]
                img_array[i+a, j+b+4*c] = [255, 255, 0]

        # Analyze box + save processed images
        Amin, Amax, Bmin, Bmax, Cmin, Cmax = cbox(img_array, ANx, ANy)
        img2_array = pbox(img_array.copy(), ANx, ANy)
        img2 = Image.fromarray(img2_array)
        img2.save(f"Processed_{filename}")

        # Apply color filtering
        img3_array = rbox(img_array.copy(), Xmax, Ymax, Amin, Amax, Bmin, Bmax, Cmin, Cmax)
        img3 = Image.fromarray(img3_array)
        img3.save(f"Postprocessed_{filename}")

        print(f"Processed and saved: Processed_{filename}, Postprocessed_{filename}")
        print(f"Color ranges: A({Amin}-{Amax}), B({Bmin}-{Bmax}), C({Cmin}-{Cmax})")

        # Wait before next capture
        time.sleep(5)

except KeyboardInterrupt:
    print("Stopping camera...")
    picam2.stop()
