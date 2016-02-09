import sys
#sys.path.insert(0, '../')
from camera import Camera
from calibrate import step
import math
from matplotlib import pyplot as plt
import numpy as np
import cv2

from socket import gethostname
from colorsHSV import *
computer_name = gethostname().split('.')[0]

def nothing(x):
    pass

# HSV Colors
WHITE_LOWER = np.array([1, 0, 100])
WHITE_HIGHER = np.array([36, 255, 255])

BLUE_LOWER = np.array([105, 140, 140])
BLUE_HIGHER = np.array([120, 255, 255])

CYAN_LOWER = np.array([80, 110, 110])
CYAN_HIGHER = np.array([100, 255, 255])

PINK_LOWER = np.array([150, 110, 110]) 
PINK_HIGHER = np.array([175, 255, 255])

RED_LOWER = np.array([0, 190, 190]) 
RED_HIGHER = np.array([4, 255, 255])

MAROON_LOWER = np.array([176, 190, 190]) 
MAROON_HIGHER = np.array([180, 255, 255])

GREEN_LOWER = np.array([60, 110, 110])
GREEN_HIGHER = np.array([75, 255, 255])

BRIGHT_GREEN_LOWER = np.array([50, 170, 170])
BRIGHT_GREEN_HIGHER = np.array([55, 255, 255])

YELLOW_LOWER = np.array([33, 190, 190])
YELLOW_HIGHER = np.array([43, 255, 255])

c = Camera()
num_of_pink_dots = 0
while(1):

	frame = c.get_frame()

	blur = cv2.GaussianBlur(frame,(11,11), 0)

	hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

	yellow_mask = cv2.inRange(hsv, color_range[(computer_name, 'yellow')][0], color_range[(computer_name, 'yellow')][1])
	pink_mask = cv2.inRange(hsv, color_range[(computer_name, 'pink')][0], color_range[(computer_name, 'pink')][1])
	green_mask = cv2.inRange(hsv, color_range[(computer_name, 'bright_green')][0], color_range[(computer_name, 'bright_green')][1])
	cyan_mask = cv2.inRange(hsv, color_range[(computer_name, 'bright_blue')][0], color_range[(computer_name, 'bright_blue')][1])
	blue_mask = cv2.inRange(hsv, color_range[(computer_name, 'blue')][0], color_range[(computer_name, 'blue')][1])
	red_mask = cv2.inRange(hsv, color_range[(computer_name, 'red')][0], color_range[(computer_name, 'red')][1])
	maroon_mask = cv2.inRange(hsv, color_range[(computer_name, 'maroon')][0], color_range[(computer_name, 'maroon')][1])
	red = cv2.bitwise_or(red_mask, maroon_mask)
	haha = cv2.bitwise_or(green_mask, cyan_mask)
	
	cv2.imshow('red', red)
	cv2.imshow('pink_mask', pink_mask)
	cv2.imshow('green_mask', green_mask)
	cv2.imshow('pink_mask', pink_mask)
	cv2.imshow('cyan_mask', cyan_mask)
	cv2.imshow('blue_mask', blue_mask)
	cv2.imshow('yellow_mask', yellow_mask)

	yellow_ret, yellow_thresh = cv2.threshold(yellow_mask,127,255,cv2.THRESH_BINARY)
	pink_ret, pink_thresh = cv2.threshold(pink_mask,127,255,cv2.THRESH_BINARY)
	green_ret, green_thresh = cv2.threshold(green_mask,127,255,cv2.THRESH_BINARY)
	_, bright_blue_thresh = cv2.threshold(cyan_mask,127,255,cv2.THRESH_BINARY)
	red_ret, red_thresh = cv2.threshold(red,127,255,cv2.THRESH_BINARY)
	blue_ret, blue_thresh = cv2.threshold(blue_mask,127,255,cv2.THRESH_BINARY)


	_, yellow_contours, _ = cv2.findContours(yellow_thresh, 1, 2)
	_, pink_contours, _ = cv2.findContours(pink_thresh, 1, 2)
	_, green_contours, _ = cv2.findContours(green_thresh, 1, 2)
	_, cyan_contours, _ = cv2.findContours(bright_blue_thresh, 1, 2)
	_, red_contours, _ = cv2.findContours(red_thresh, 1, 2)
	_, blue_contours, _ = cv2.findContours(blue_thresh, 1, 2)
	
	#print len(green_contours)
	pink_balls = []
	green_balls = []
	for i in range(0, len(red_contours)):
		cnt = red_contours[i]
		M = cv2.moments(cnt)
		if M['m00'] == 0 :
			continue

		# center coordinates:	
		cx = int(M['m10']/M['m00'])
		cy = int(M['m01']/M['m00'])

		(x,y),radius = cv2.minEnclosingCircle(cnt)

		center = (int(x),int(y))
		radius = int(radius)
		if radius >= 2:
			cv2.circle(frame,center,7,(0,0,255),2)

	for i in range(0, len(blue_contours)):
		cnt = blue_contours[i]
		M = cv2.moments(cnt)
		if M['m00'] == 0 :
			continue

		# center coordinates:	
		cx = int(M['m10']/M['m00'])
		cy = int(M['m01']/M['m00'])

		(x,y),radius = cv2.minEnclosingCircle(cnt)

		center = (int(x),int(y))
		radius = int(radius)
		if radius >= 2:
			cv2.circle(frame,center,7,(255,0,0),2)
			
	for i in range(0, len(pink_contours)):
		cnt = pink_contours[i]
		M = cv2.moments(cnt)
		if M['m00'] == 0 :
			continue

		# center coordinates:	
		cx = int(M['m10']/M['m00'])
		cy = int(M['m01']/M['m00'])

		(x,y),radius = cv2.minEnclosingCircle(cnt)

		center = (int(x),int(y))
		pink_balls.append(center)
		radius = int(radius)
		if radius >= 2:
			cv2.circle(frame,center,radius,(147,20,255),2)
		
	for i in range(0, len(green_contours)):
		cnt = green_contours[i]
		M = cv2.moments(cnt)
		if M['m00'] == 0 :
			continue

		# center coordinates:	
		cx = int(M['m10']/M['m00'])
		cy = int(M['m01']/M['m00'])

		(x,y),radius = cv2.minEnclosingCircle(cnt)

		center = (int(x),int(y))
		green_balls.append(center)
		radius = int(radius)
		if radius >= 2:
			cv2.circle(frame,center,radius,(0,255,0),2)
	
	for i in range(0, len(cyan_contours)):
		cnt = cyan_contours[i]
		M = cv2.moments(cnt)
		if M['m00'] == 0 :
			continue

		# center coordinates:	
		cx = int(M['m10']/M['m00'])
		cy = int(M['m01']/M['m00'])

		(x,y),radius = cv2.minEnclosingCircle(cnt)

		center = (int(x),int(y))
		radius = int(radius)
		if radius >= 2:
			cv2.circle(frame,center,7,(255,255,0),2)

	for i in range(0, len(yellow_contours)):
		cnt = yellow_contours[i]
		M = cv2.moments(cnt)
		if M['m00'] == 0 :
			continue

		# center coordinates:	
		cx = int(M['m10']/M['m00'])
		cy = int(M['m01']/M['m00'])

		'''
		print "-----------------------"
		#---------this is for detecting top plate-----------
		x,y,w,h = cv2.boundingRect(cnt)
		print x, y, w, h
		#yellow_mask = cv2.rectangle(yellow_mask,(x,y),(100,100),(0,255,0),2)
		rect = cv2.minAreaRect(cnt)
		box = cv2.boxPoints(rect)
		box = np.int0(box)
		#mask = cv2.drawContours(mask,[box],0,(0,0,255),2)
		cv2.rectangle(frame, (x-10,y-10),(x+w+5,y+h+5),(0,255,0),2)
		'''
		num_of_pink = 0
		num_of_green = 0
		(x,y),radius = cv2.minEnclosingCircle(cnt)

		for i in range(0, len(pink_balls)):
			if (math.sqrt(((x-pink_balls[i][0])**2)+(y-pink_balls[i][1])**2) < 17):
				num_of_pink += 1
		for i in range(0, len(green_balls)):
			if (math.sqrt(((x-green_balls[i][0])**2)+(y-green_balls[i][1])**2) < 17):
				num_of_green += 1		

		center = (int(x),int(y))
		radius = int(radius)
		if num_of_pink > 1 and num_of_green < 2:
			cv2.putText(frame,'OUR',(center[0]-15, center[1]+30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, 90)
			cv2.putText(frame,'DEFENDER',(center[0]-30, center[1]+40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, 90)
		if num_of_pink < 2 and num_of_green > 1:
			cv2.putText(frame,'OUR',(center[0]-15, center[1]+30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, 220)
			cv2.putText(frame,'ATTACKER',(center[0]-30, center[1]+40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, 220)
		if radius >= 2:	
			cv2.circle(frame,center,20,(90,0,0),2)	

	
	#cv2.circle(frame,(320,240),5,(0,0,0),2)	
    # Bitwise-AND mask  and original image
	#res = cv2.bitwise_and(frame,frame, mask= mask)
	#cv2.imshow('hsv', hsv) 
	#cv2.imshow('blurred lines', blur)
	cv2.imshow('frame',frame)
	#cv2.imwrite('frame.png', frame)
	#cv2.imwrite('transform.png', frame)
	#cv2.imwrite('b.png', frame)
	#cv2.imshow('mask',mask)
	#cv2.imshow('res',res)
	
	k = cv2.waitKey(5) & 0xFF
	if k == 27:
		break

c.close() 
cv2.destroyAllWindows()       
