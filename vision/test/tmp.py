import sys
sys.path.insert(0, '/afs/inf.ed.ac.uk/user/s12/s1237357/Desktop/group3-4-vision/vision')
sys.path.insert(0, '/afs/inf.ed.ac.uk/user/s12/s1237357/Desktop/group3-4-vision/vision/config')

from camera import Camera
from calibrate import step
import math
from matplotlib import pyplot as plt
import numpy as np
import cv2

c = Camera()

properties={'POS_MSEC' : 0, 
	'POS_FRAMES' : 1,
	'FRAME_WIDTH' : 3, 
	'FRAME_HEIGHT' : 4, 
	'PROP_FPS' : 5,      
	'PROP_MODE' : 9, 
	'BRIGHTNESS' : 10,  
	'CONTRAST' : 11,
	'COLOR' : 12, 
	'HUE' : 13
}
cap = cv2.VideoCapture(0)
#cap.set(properties['BRIGHTNESS'], 0.5)
#cap.set(properties['HUE'], 0.5)
for i in properties:
	print i +" = "+ str(cap.get(properties[i]))
while True:
	

	#frame = step(c.get_frame())
    #cv2.circle(frame, (320,240), 5, (255,0,0), 1)
    #cal.show_frame(frame)
    #cv2.imwrite('useful.png',frame)
     # Convert BGR to HSV

	#cap = cv2.VideoCapture(0)
	#for prop in properties:
		#val=cap.get(eval("cv2."+prop))
		#print prop+": "+str(val)
	#brightness = cap.get(properties['BRIGHTNESS'])
	#print brightness

	#frame.set(properties['BRIGHTNESS'], 0.5)
	ret, img = cap.read()
	print "RET is: " + str(ret)
	cv2.imshow('img', img)
	#cv2.imshow('frame', img)
	#hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV

	#lower_blue = np.array([110,50,50])
	#upper_blue = np.array([130,255,255])

    # Threshold the HSV image to get only blue colors
	#mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Bitwise-AND mask and original image
	#res = cv2.bitwise_and(frame,frame, mask= mask)

	#cv2.imshow('frame',frame)
	#cv2.imshow('mask',mask)
	#cv2.imshow('res',res)

	k = cv2.waitKey(5) & 0xFF
	if k == 27:
		break

	#cv2.destroyAllWindows()

    #if cv2.waitKey(1) & 0xFF == ord('q'):
      #break

c.close()
cv2.destroyAllWindows()
