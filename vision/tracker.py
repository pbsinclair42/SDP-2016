from camera import Camera
from calibrate import step
from matplotlib import pyplot as plt
import numpy as np
import cv2

# HSV Colors
WHITE_LOWER = np.array([1, 0, 100])
WHITE_HIGHER = np.array([36, 255, 255])

BLUE_LOWER = np.array([70, 50, 50])
BLUE_HIGHER = np.array([160, 255, 255])

RED_LOWER = np.array([0, 175, 90])
RED_HIGHER = np.array([230, 255, 255])

YELLOW_LOWER = np.array([9, 50, 50])
YELLOW_HIGHER = np.array([11, 255, 255])

c = Camera()

def get_ball_coordinates(ballColor):	

	# get the frame from video capture
	frame = step(c.get_frame())
	# apply Gaussian blurring to remove noise
	blur = cv2.GaussianBlur(frame,(19,19), 0)

	# convert RGB color scale into HSV
	hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
	
	# define range of ball color in HSV
	if ballColor == 'RED':
		mask = cv2.inRange(hsv, RED_LOWER, RED_HIGHER)
	elif ballColor == 'BLUE':
		mask = cv2.inRange(hsv, BLUE_LOWER, BLUE_HIGHER)

	ret,thresh = cv2.threshold(mask,127,255,0)

	_, contours, _ = cv2.findContours(thresh, 1, 2)

	''' need to check how many objects (balls/noise) are being detected
		if more than one, probably need to take the coordinates of the bigger contours
		ttherefore we need to use arclength function'''

	# assume there is only one ball on the pitch and there is no noise:
	cnt = contours[0]
	M = cv2.moments(cnt)

	if M['m00'] == 0:
		pass

	cx = int(M['m10']/M['m00'])
	cy = int(M['m01']/M['m00'])

	(x,y),radius = cv2.minEnclosingCircle(cnt)
	center = (int(x),int(y))
	radius = int(radius)

	return center	
	
def opponent_defender_coordinates():
	pass

def opponent_attacker_coordinates():
	pass

def our_defender_coordinates():
	pass

def our_attacker_coordinates():
	pass				