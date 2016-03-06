import cv2
import cPickle
import numpy as np

img = cv2.imread('perspective.png')
data = []
filename = open('points.txt', 'r+')

# mouse callback function
def draw(event,x,y,flags,param):
    
    if event == cv2.EVENT_LBUTTONDBLCLK:
        data.append((x,y))
        print data
        print len(data)
        if len(data) % 2 == 0:
            filename.write("("+ str(x)+", "+str(y)+")\n")
        else:
            filename.write("("+ str(x)+", "+str(y)+") -> ")
        cv2.circle(img,(x,y),5,(255,0,0),-1)

# Create a black image, a window and bind the function to window

cv2.namedWindow('image')
cv2.setMouseCallback('image',draw)

while(1):
    cv2.imshow('image',img)
    if cv2.waitKey(20) & 0xFF == 27:
        break
cv2.destroyAllWindows()
