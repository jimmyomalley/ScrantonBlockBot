import cv2
import numpy as np
import time
from gpiozero import LED
from picamera2 import Picamera2

# -----------------------------
# Raspberry Pi GPIO setup
# -----------------------------
led1 = LED(17)   # Right Motor Forward
led2 = LED(27)   # Right Motor Reverse
led3 = LED(23)   # Left Motor Forward
led4 = LED(24)   # Left Motor Reverse

def stop():
    led1.off(); led2.off(); led3.off(); led4.off()

def move_forward():
    led1.on(); led2.off(); led3.on(); led4.off()

def move_backward():
    led1.off(); led2.on(); led3.off(); led4.on()

def turn_left():
    led1.off(); led2.on(); led3.on(); led4.off()

def turn_right():
    led1.on(); led2.off(); led3.off(); led4.on()

# -----------------------------
# Camera setup
# -----------------------------
picam2 = Picamera2()
camera_config = picam2.create_still_configuration(main={"size": (640, 480)})  # smaller = faster
picam2.configure(camera_config)
picam2.start()
time.sleep(2)

# -----------------------------
# Color ranges (HSV)
# -----------------------------
color_ranges = {
    "red1":   (np.array([0, 120, 70]),   np.array([10, 255, 255])),
    "red2":   (np.array([170, 120, 70]), np.array([180, 255, 255])),  # red wraps around hue
    "green":  (np.array([40, 70, 70]),   np.array([80, 255, 255])),
    "blue":   (np.array([90, 70, 70]),   np.array([130, 255, 255])),
    "yellow": (np.array([20, 100, 100]), np.array([35, 255, 255]))
}

# -----------------------------
# Camera / movement parameters
# -----------------------------
FOV_HORIZONTAL = 62.2  # Raspberry Pi Camera v2 horizontal FOV (deg)

# Calibration table (pixel height -> distance cm)
calibration = {
    50: 14,
    100: 21,
    150: 29,
    200: 47
}

def interpolate_distance(pixel_height):
    """Estimate distance from pixel height using linear interpolation."""
    pixels = sorted(calibration.keys())

    if pixel_height <= pixels[0]:
        return calibration[pixels[0]]
    if pixel_height >= pixels[-1]:
        return calibration[pixels[-1]]

    for i in range(len(pixels) - 1):
        p1, p2 = pixels[i], pixels[i + 1]
        if p1 <= pixel_height <= p2:
            d1, d2 = calibration[p1], calibration[p2]
            return d1 + (d2 - d1) * ((pixel_height - p1) / (p2 - p1))

    return None

# -----------------------------
# Choose target color
# -----------------------------
target_color = "red"   # change to "green", "blue", "yellow" as needed

# -----------------------------
# Main loop
# -----------------------------
try:
    while True:
        frame = picam2.capture_array()
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

        # Get mask for chosen color
        mask = None
        if target_color == "red":
            mask1 = cv2.inRange(hsv, color_ranges["red1"][0], color_ranges["red1"][1])
            mask2 = cv2.inRange(hsv, color_ranges["red2"][0], color_ranges["red2"][1])
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            lower, upper = color_ranges[target_color]
            mask = cv2.inRange(hsv, lower, upper)

        # Find contours of detected object
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Use the largest contour
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            cx = x + w // 2
            cy = y + h // 2

            # Angle (in degrees)
            center_x = frame.shape[1] // 2
            angle = (cx - center_x) * (FOV_HORIZONTAL / frame.shape[1])

            # Distance using calibration table
            distance = interpolate_distance(h) if h > 0 else None

            print(f"Color: {target_color}, Angle: {angle:.2f} deg, Height: {h}px, Distance: {distance:.2f} cm")

            # -----------------------------
            # Movement logic
            # -----------------------------
            if distance is None:
                stop()
            elif distance < 15:  # stop if close enough
                stop()
            elif abs(angle) < 5:
                move_forward()
            elif angle < -5:
                turn_left()
            elif angle > 5:
                turn_right()
        else:
            stop()

        time.sleep(0.1)

except KeyboardInterrupt:
    stop()
    picam2.stop()
    print("Program stopped.")
