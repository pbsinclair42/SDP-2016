import sys
from camera import Camera
from calibrate import step
import math

import numpy as np
import cv2

c = Camera()
img = c.get_frame()

#img = cv2.imread('Pitch.png')

hsv_range = {}
bgr = {
    'blue' : [],
    'bright_blue' : [],
    'pink' : [],
    'green' : [],
    'yellow' : []
}


color = ''

def nothing(x):
    pass
'''
denoises mask, so that colors will not flicker
'''
def denoiseMask(mask):
    kernel =  cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    po = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    po = cv2.morphologyEx(po, cv2.MORPH_OPEN, kernel)
    return po

'''
gets pixel value from img on coordinates (x, y)
'''
def getPixelValue(img, x, y):
    # return pixel value at (x,y): [B,G,R] 
    print img[x,y]
    return img[x,y]

'''
takes the list of list (aka BGR values of all dots) 
and returns average
'''
def averageValue(array):
    print len(array)
    print array
    b, g, r = 0, 0, 0
    for item in array:
        b += item[0]
        g += item[1]
        r += item[2]
    print b, g, r    
    return math.floor(b/len(array)), math.floor(g/len(array)), math.floor(r/len(array))
'''
takes color value in BGR and converts it into HSV colorspace
'''
def getHueValue(array):
    hue = np.uint8([[[array[0],array[1],array[2]]]])
    hsv_hue = cv2.cvtColor(hue,cv2.COLOR_BGR2HSV)
    return hsv_hue

'''
function which is responsible for recording mouse clicks
and getting their pixel values and appending them to the list
'''
def getColorValues(event,x,y,flags,param):
    global color
    if event == cv2.EVENT_LBUTTONDOWN:
        if color == 'blue':
            bgr['blue'].append(getPixelValue(img, y, x).tolist())
            cv2.circle(img,(x,y),5,(255,0,0),-1) 
           
        elif color == 'bright_blue':
            bgr['bright_blue'].append(getPixelValue(img, y, x).tolist()) 
            cv2.circle(img,(x,y),5,(255,255,0),-1) 
                  
        elif color == 'pink':
            bgr['pink'].append(getPixelValue(img, y, x).tolist())
            cv2.circle(img,(x,y),5,(255,0,255),-1) 
            
        elif color == 'green':
            bgr['green'].append(getPixelValue(img, y, x).tolist())
            cv2.circle(img,(x,y),5,(0,255,0),-1) 
            
        elif color == 'yellow':
            bgr['yellow'].append(getPixelValue(img, y, x).tolist())
            cv2.circle(img,(x,y),5,(0,255,255),-1) 
                  
'''
getThresholds() automatically thresholds colors only by clicking on the current feed
Function returns 'hsv_range' - dictionary that contains all needed thresholds
for these colors: red, maroon, green (aka bright_green), pink, yellow, blue and light_blue
'''
def getThresholds():
    global color
    hsv_range = {}
    hsv_range['red'] = ( np.array([0, 190, 190]), np.array([5, 255, 255]) )
    hsv_range['maroon'] = ( np.array([175, 190, 190]), np.array([180, 255, 255]) )
    
    print "What colours do you want to calibrate?"
    print "Click once the image after pressing the following: \n 'b' -> blue \n 'c' -> bright_blue \n 'p' -> pink \n 'g' -> green \n 'y' -> yellow"
    print "If you want to redo, press 'r'"
    cv2.namedWindow('image')
    cv2.setMouseCallback('image',getColorValues)

    while(1):
        cv2.imshow('image',img)
        # keys for colours: 
        k = cv2.waitKey(1) & 0xFF
        if k == ord('b'):
            print "Click on BLUE"
            color = 'blue'
        elif k == ord('c'):
            print "Click on BRIGHT BLUE"            
            color = 'bright_blue'  
        elif k == ord('p'):
            print "Click on PINK"
            color = 'pink'
        elif k == ord('g'):
            print "Click on GREEN"
            color = 'green'
        elif k == ord('y'):
            print "Click on YELLOW"
            color = 'yellow'
        if k == ord('r'):
            inp = raw_input("Type which color you want redo: \n")
            print "will redo " + inp
            bgr[inp] = []
            print "Click corresponding color character again\n"                  
        elif k == 27:
            break

    print "Destroying all windows"        
    cv2.destroyAllWindows()
    c.close()     
    print "Averaging BGR values..."
    for colors in bgr:
        if (len(bgr[colors]) != 0):
            h = getHueValue(averageValue(bgr[colors]))
            value = h[0][0][0]
            hsv_range[colors] = ( np.array([value-10, 140, 140]), np.array([value+10, 255, 255]) )
    return hsv_range        
