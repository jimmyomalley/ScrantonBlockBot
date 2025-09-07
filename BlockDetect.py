import cv2
import numpy as np
from picamera2 import Picamera2
from gpiozero import Motor,Robot,LED 
import RPi.GPIO as GPIO
from time import sleep
import time as time
import serial

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

# Define your color ranges
green_lower = np.array([40,170,90], np.uint8)
green_upper = np.array([102,255,220], np.uint8)

red_lower = np.array([136,87,111], np.uint8)
red_upper = np.array([180,255,255], np.uint8)

blue_lower = np.array([94,185,170], np.uint8)
blue_upper = np.array([120,255,255], np.uint8)

# Initialize PiCamera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280, 720)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.IN)
GPIO.setup(27,GPIO.IN)


###########################################################################Defining Functions#######################################################################

def detect_single_color(imageFrame, color_name, lower_range, upper_range, color_display):
    x=0
    y=0
    w=0
    h=0
    hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV)
    color_mask = cv2.inRange(hsvFrame, lower_range, upper_range)

    kernel = np.ones((5, 5), "uint8")
    color_mask = cv2.dilate(color_mask, kernel)
    result = cv2.bitwise_and(imageFrame, imageFrame, mask=color_mask)

    contours, hierarchy = cv2.findContours(color_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area > 800:
            x, y, w, h = cv2.boundingRect(contour)
            imageFrame = cv2.rectangle(imageFrame, (x, y), (x + w, y + h), color_display, 2)
            cv2.putText(imageFrame, f"{color_name}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color_display)
        

    return imageFrame,x,y,w,h

def cntr_colorH(color,color_lower,color_upper):
	xc=0
	wc=0
	angle = 90
	while(xc == 0 and wc == 0):
		set_servo("H",angle)
		im = picam2.capture_array()
		im = cv2.flip(im,0)
		im = cv2.flip(im,1)
		blur_image = cv2.GaussianBlur(im,(7,7),0)
		result_frame,xc,yc,wc,hc = detect_single_color(blur_image, color, color_lower, color_upper, (0, 255, 0))
		block_center = xc + wc/2
		
		if block_center >= 700 and angle>0:
			angle=angle-5
			set_servo("H",angle)
			print("Block detected on right, panning right")
			xc=0
			wc=0
		elif block_center>500 and block_center<700:
			print("Block detected in center")
		else:
			angle=angle+5
			set_servo("H",angle)
			print("Block detected on left, panning left")
			xc=0
			wc=0
		if angle==180:
			angle=0
		
	return yc,hc,angle
			
def set_servo(direction,angle):
	send_message(direction+str(angle))

        
def send_message(message):
	ser.write(message.encode('utf-8'))
	print(f"Sent: {message}")
	
def receive_message():
    if ser.in_waiting >0:
        response =ser.readline().decode('utf-8').strip()
        return response
    return None
    
def get_distance(yc,hc):
	dist = (yc+hc)/700
	dist = 80-(74*dist)
	print("The object is "+str(dist)+" inches away")
	if dist <= 48:
		dtype = "A"
	elif dist <= 72:
		dtype = "C"
	else:
		dtype = "E"
	return dtype


####################################################################Searching for blocks###################################################################

en=1
while True:
	if en==1:
		send_message("start")
		print("Scanning procedure begun for Green")
		yc,hc,angle=cntr_colorH("Green", green_lower, green_upper)
		dtype = get_distance(yc,hc)
		send_message("IG"+dtype+str(angle))
		time.sleep(3)
		
		print("Scanning procedure begun for Red")
		yc,hc,angle=cntr_colorH("Red", red_lower, red_upper)
		dtype = get_distance(yc,hc)
		send_message("IR"+dtype+str(angle))
		time.sleep(3)
		
		print("Scanning procedure begun for Blue")
		yc,hc,angle=cntr_colorH("Blue", blue_lower, blue_upper)
		dtype = get_distance(yc,hc)
		send_message("IB"+dtype+str(angle))
		
	en=0
	im = picam2.capture_array()
	im = cv2.flip(im,0)
	im = cv2.flip(im,1)
	blur_image = cv2.GaussianBlur(im,(7,7),0)
	cv2.imshow("Block picker in Real-Time",blur_image)
	
