import time
import string
import random
import cv2
import numpy as np
from picamera2 import Picamera2
from PIL import Image
# Function to generate a random 4-character string
def random_filename(length=4):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def compute_edge_gap(img_bgr, edge='bottom', min_area=1000):
    """
    Returns gap_in_pixels, annotated_bgr
    - img_bgr: OpenCV BGR image
    - edge: 'bottom' | 'top' | 'left' | 'right'
    - min_area: ignore tiny contours (noise)
    """
    h, w = img_bgr.shape[:2]

    # 1) Preprocess to find strong edges
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    # Light blur to reduce noise; increase kernel size if noisy
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # Canny edges; tweak these if needed
    edges = cv2.Canny(blur, 60, 180)

    # Close small gaps in edges (helps make contours solid)
    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=1)

    # 2) Find contours
    cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# Filter out tiny contours
    cnts = [c for c in cnts if cv2.contourArea(c) > min_area]
    if not cnts:
        # No object found; return 0 and original image
        return 0, img_bgr.copy()

    # Heuristic: choose the contour closest to the requested edge
    def distance_to_edge(cnt):
        if edge == 'bottom':
            y_max = cnt[:, 0, 1].max()
            return h - y_max
        elif edge == 'top':
            y_min = cnt[:, 0, 1].min()
            return y_min
        elif edge == 'left':
            x_min = cnt[:, 0, 0].min()
            return x_min
        elif edge == 'right':
            x_max = cnt[:, 0, 0].max()
            return w - x_max
        else:
            raise ValueError("edge must be 'bottom', 'top', 'left', or 'right'")

    # Pick the object that minimizes the gap to that edge (closest object)
    target_cnt = min(cnts, key=distance_to_edge)
    gap = int(round(distance_to_edge(target_cnt)))

    # 3) Make an annotated image for visual verification
    annotated = img_bgr.copy()
    cv2.drawContours(annotated, [target_cnt], -1, (0, 255, 0), 2)

    # Compute the extremal point we measured from; also draw a line to the edge
    xs = target_cnt[:, 0, 0]
    ys = target_cnt[:, 0, 1]
    if edge == 'bottom':
        y_max = ys.max()
        x_at = int(xs[ys.argmax()])  # x at bottom-most point
        cv2.line(annotated, (x_at, y_max), (x_at, h-1), (255, 0, 0), 2)
        cv2.putText(annotated, f"Gap: {gap}px (bottom)", (10, h-15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    elif edge == 'top':
        y_min = ys.min()
        x_at = int(xs[ys.argmin()])
        cv2.line(annotated, (x_at, 0), (x_at, y_min), (255, 0, 0), 2)
        cv2.putText(annotated, f"Gap: {gap}px (top)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    elif edge == 'left':
        x_min = xs.min()
        y_at = int(ys[xs.argmin()])
        cv2.line(annotated, (0, y_at), (x_min, y_at), (255, 0, 0), 2)
        cv2.putText(annotated, f"Gap: {gap}px (left)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    elif edge == 'right':
        x_max = xs.max()
        y_at = int(ys[xs.argmax()])
        cv2.line(annotated, (x_max, y_at), (w-1, y_at), (255, 0, 0), 2)
        cv2.putText(annotated, f"Gap: {gap}px (right)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    return gap, annotated

# ---- Your existing capture flow ----
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

# Also grab the frame into numpy for processing
image_array = picam2.capture_array()  # RGB array
picam2.stop()

# Convert RGB (Picamera2) -> BGR (OpenCV)
img_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)

# Choose which edge to measure from:
EDGE = 'bottom'  # 'bottom' | 'top' | 'left' | 'right'

gap_px, annotated = compute_edge_gap(img_bgr, edge=EDGE, min_area=1500)
print(f"Gap from {EDGE} edge to object: {gap_px} pixels")

# Convert pixels to centimeters
gap_cm = gap_px / 2.067

print(f"Gap from {EDGE} edge to object: {gap_px} pixels ({gap_cm:.2f} cm)")

# Save an annotated image so you can verify visually
annotated_name = filename.replace(".jpg", f"_annotated_{EDGE}.jpg")
cv2.imwrite(annotated_name, annotated)
print(f"Annotated preview saved as {annotated_name}")

