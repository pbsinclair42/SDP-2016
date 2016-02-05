from camera import Camera
from calibrate import *
import cv2

cal = Calibrate()
c = Camera()

def do_thing():

	while True:
		frame = cal.step(c.get_frame())
    #cv2.circle(frame, (320,240), 5, (255,0,0), 1)
    #cal.show_frame(frame)
    #cv2.imwrite('useful.png',frame)
     # Convert BGR to HSV
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV

		lower_blue = np.array([110,50,50])
		upper_blue = np.array([130,255,255])

    # Threshold the HSV image to get only blue colors
		mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Bitwise-AND mask and original image
		res = cv2.bitwise_and(frame,frame, mask= mask)

		cv2.imshow('frame',frame)
		cv2.imshow('mask',mask)
		cv2.imshow('res',res)

		k = cv2.waitKey(5) & 0xFF
		if k == 27:
			break

	#cv2.destroyAllWindows()

    #if cv2.waitKey(1) & 0xFF == ord('q'):
      #break

	c.close()
	cv2.destroyAllWindows()
