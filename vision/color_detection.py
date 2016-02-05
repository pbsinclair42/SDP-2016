from camera import Camera
from calibrate import step
from matplotlib import pyplot as plt
import numpy as np
import cv2


def nothing(x):
    pass

# HSV Colors
WHITE_LOWER = np.array([1, 0, 100])
WHITE_HIGHER = np.array([36, 255, 255])

BLUE_LOWER = np.array([70, 50, 50])
BLUE_HIGHER = np.array([160, 255, 255])


PINK_LOWER = np.array([155, 100, 100]) 
PINK_HIGHER = np.array([175, 255, 255])

RED_LOWER = np.array([0, 110, 100]) 
RED_HIGHER = np.array([5, 255, 255])

GREEN_LOWER = np.array([50, 110, 110])
GREEN_HIGHER = np.array([70, 255, 255])

BRIGHT_GREEN_LOWER = np.array([40, 110, 110])
BRIGHT_GREEN_HIGHER = np.array([55, 255, 255])

YELLOW_LOWER = np.array([25, 100, 100])
YELLOW_HIGHER = np.array([40, 255, 255])

c = Camera()

while(1):

	frame = step(c.get_frame())

	blur = cv2.GaussianBlur(frame,(19,19), 0)
	hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

	#mask1 = cv2.inRange(hsv, RED_LOWER1, RED_HIGHER1)
	mask = cv2.inRange(hsv, GREEN_LOWER, GREEN_HIGHER)
	#mask = cv2.bitwise_and(mask1, mask1, mask2)
	ret,thresh = cv2.threshold(mask,127,255,0)

	_, contours, _ = cv2.findContours(thresh, 1, 2)

	# len(contours) represents the number of objects detected
	print len(contours)
	for i in range(0, len(contours)):
		cnt = contours[i]
		M = cv2.moments(cnt)
		if M['m00'] == 0 :
			continue

		# center coordinates:	
		cx = int(M['m10']/M['m00'])
		cy = int(M['m01']/M['m00'])
		
		#---------this is for detecting top plate-----------
		x,y,w,h = cv2.boundingRect(cnt)
		mask = cv2.rectangle(mask,(x,y),(x+w,y+h),(0,255,0),2)
		rect = cv2.minAreaRect(cnt)
		box = cv2.boxPoints(rect)
		box = np.int0(box)
		mask = cv2.drawContours(mask,[box],0,(0,0,255),2)
		cv2.rectangle(frame, (x,y),(x+w,y+h),(0,255,0),2)
		'''
		(x,y),radius = cv2.minEnclosingCircle(cnt)
		print(str(x) + "  :  " + str(y))
		center = (int(x),int(y))
		radius = int(radius)
		cv2.circle(frame,center,radius,(0,255,0),2)
		'''
	
    # Bitwise-AND mask  and original image
	res = cv2.bitwise_and(frame,frame, mask= mask)
	cv2.imshow('hsv', hsv) 
	cv2.imshow('blurred lines', blur)
	cv2.imshow('frame',frame)
	cv2.imshow('mask',mask)
	cv2.imshow('res',res)
	
	k = cv2.waitKey(5) & 0xFF
	if k == 27:
		break

c.close() 
cv2.destroyAllWindows()       