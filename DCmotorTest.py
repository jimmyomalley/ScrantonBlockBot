import time as time

from gpiozero import Motor,Robot 
from time import sleep

robot= Robot(left=Motor(19,13), right=Motor(5,6))
while True:
	robot.forward(1)
	sleep(2)
	print("hello world")
	robot.backward(1)                                              
	sleep(2)
	print("worked")
	robot.right(1)
	sleep(10)

