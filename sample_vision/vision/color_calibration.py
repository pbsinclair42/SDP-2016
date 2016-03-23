import sys
from camera import Camera
import argparse
import math
import os
import json
import numpy as np
import cv2
from tools import *

bgr = {
    'blue' : [],
    'bright_blue' : [],
    'pink' : [],
    'green' : [],
    'yellow' : []
}

circle_coords = []
color = ''

def nothing(x):
    pass

'''
denoises mask, so that colors will not flicker
'''
def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p",
                        help="Pitch number", 
                        required=True, 
                        choices=["0", "1"])
    parser.add_argument("-t",
                        help="Reading picture or live camera feed?",
                        required=True,
                        choices=["0", "1"])
    return parser.parse_args()

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
    b, g, r = 0, 0, 0
    for item in array:
        b += item[0]
        g += item[1]
        r += item[2]  
    return math.floor(b/len(array)), math.floor(g/len(array)), math.floor(r/len(array))

'''
takes color value in BGR and converts it into HSV colorspace
'''
def getHueValue(array):
    hue = np.uint8([[[array[0],array[1],array[2]]]])
    hsv_hue = cv2.cvtColor(hue,cv2.COLOR_BGR2HSV)
    return hsv_hue

def drawCircle(array, img):
    for tuples in array:
        cv2.circle(img,tuples,5,(255,0,0),3)

'''
function which is responsible for recording mouse clicks
and getting their pixel values and appending them to the list
'''
def getColorValues(event,x,y,flags,param):
    global color
    global img
    global circle_coords
    if event == cv2.EVENT_LBUTTONDOWN:
        if color == 'blue':
            bgr['blue'].append(getPixelValue(img, y, x).tolist())
            circle_coords.append((x,y))
               
        elif color == 'bright_blue':
            bgr['bright_blue'].append(getPixelValue(img, y, x).tolist()) 
            circle_coords.append((x,y))

        elif color == 'pink':
            bgr['pink'].append(getPixelValue(img, y, x).tolist())
            circle_coords.append((x,y))
                
        elif color == 'green':
            bgr['green'].append(getPixelValue(img, y, x).tolist())
            circle_coords.append((x,y))
                
        elif color == 'yellow':
            bgr['yellow'].append(getPixelValue(img, y, x).tolist())
            circle_coords.append((x,y))


'''
getThresholds() automatically thresholds colors only by clicking on the current feed
Function returns 'hsv_range' - dictionary that contains all needed thresholds
for these colors: red, maroon, green (aka bright_green), pink, yellow, blue and light_blue
'''
def getThresholds(pitch, camera):
    global color
    global img
    hsv_range = {}
    hsv_range['red'] = ( np.array([0, 150, 150]), np.array([5, 255, 255]) )
    hsv_range['maroon'] = ( np.array([175, 150, 150]), np.array([180, 255, 255]) )
    
    print "What colours do you want to calibrate?"
    print "Click once on the image after pressing the following: \n 'b' -> blue \n 'c' -> bright_blue \n 'p' -> pink \n 'g' -> green \n 'y' -> yellow"
    print "If you want to redo, click corresponding color character agian."
    print "Once done with obtaining pixel values, pres ESC to proceed."
    cv2.namedWindow('image')
    cv2.setMouseCallback('image',getColorValues)

    while(1):
        img = camera.get_frame()
        cv2.imshow('image',img)

        k = cv2.waitKey(1) & 0xFF
        if k == ord('b'):
            print "Click on BLUE"
            bgr['blue'] = []
            color = 'blue'
        elif k == ord('c'):
            print "Click on BRIGHT BLUE" 
            bgr['bright_blue'] = []           
            color = 'bright_blue'  
        elif k == ord('p'):
            print "Click on PINK"
            bgr['pink'] = []
            color = 'pink'
        elif k == ord('g'):
            print "Click on GREEN"
            bgr['green'] = []
            color = 'green'
        elif k == ord('y'):
            print "Click on YELLOW"
            bgr['yellow'] = []
            color = 'yellow'                 
        elif k == 27:
            break

    print "Destroying all windows"        
    cv2.destroyAllWindows()
    print "Averaging BGR values..."
    for colors in bgr:
        if (len(bgr[colors]) != 0):
            h = getHueValue(averageValue(bgr[colors]))
            value = h[0][0][0]
            hsv_range[colors] = ( np.array([value-10, 140, 140]), np.array([value+10, 255, 255]) )
    return hsv_range        

'''
uses GUI sliding trackbars to calibrate thresholds
and returns dictionary with calibrated thresholds
'''
def calibrateThresholds(pitch, test=0):

    # keys: blue, pink, maroon, green, yellow, bright_blue, red
    c = Camera(pitch, 0, test)
    thresholds = getThresholds(pitch, c)
    calibrated_thresholds = {}
    

    for colors in thresholds:
        if colors != 'red' and colors != 'maroon': 
            cv2.namedWindow(colors)
            print "Will be calibrating: "+colors

            h_low_init = thresholds[colors][0][0]
            h_high_init = thresholds[colors][1][0]
            s_low_init = thresholds[colors][0][1]
            v_low_init = thresholds[colors][0][2]

            cv2.createTrackbar('H low',colors,h_low_init,180,nothing)
            cv2.createTrackbar('H high',colors,h_high_init,180,nothing)
            cv2.createTrackbar('S low',colors,s_low_init,255,nothing)
            cv2.createTrackbar('V low',colors,v_low_init,255,nothing)

            while(1):
                frame = c.get_frame()
                blur = cv2.GaussianBlur(frame,(11,11), 0)
                hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
                h_low = cv2.getTrackbarPos('H low',colors)
                h_high = cv2.getTrackbarPos('H high',colors)
                s_low = cv2.getTrackbarPos('S low',colors)
                v_low = cv2.getTrackbarPos('V low',colors)
                # create  mask
                mask = cv2.inRange(hsv, (h_low, s_low, v_low), (h_high, 255, 255))
                # show mask and an actual picture for comparison
                cv2.imshow(colors, denoiseMask(mask))
                cv2.imshow('actual feed', frame)
                    
                calibrated_thresholds[colors] = {'min': np.array([h_low, s_low, v_low]),'max': np.array([h_high, 255, 255]) }

                k = cv2.waitKey(1) & 0xFF
                if k == 27:
                    break  

            print colors + " was calibrated"

    print "Now RED will be calibrated which takes two different color ranges"
                          
    cv2.namedWindow('red')
    h_low_red_init = thresholds['red'][0][0]
    h_high_red_init = thresholds['red'][1][0]
    s_low_red_init = thresholds['red'][0][1]
    v_low_red_init = thresholds['red'][0][2]

    h_low_maroon_init = thresholds['maroon'][0][0]
    h_high_maroon_init = thresholds['maroon'][1][0]
    s_low_maroon_init = thresholds['maroon'][0][1]
    v_low_maroon_init = thresholds['maroon'][0][2]

    cv2.createTrackbar('H low red','red',h_low_red_init,180,nothing)
    cv2.createTrackbar('H high red','red',h_high_red_init,180,nothing)
    cv2.createTrackbar('S low red','red',s_low_red_init,255,nothing)
    cv2.createTrackbar('V low red','red',v_low_red_init,255,nothing)

    cv2.createTrackbar('H low maroon','red',h_low_maroon_init,180,nothing)
    cv2.createTrackbar('H high maroon','red',h_high_maroon_init,180,nothing)
    cv2.createTrackbar('S low maroon','red',s_low_maroon_init,255,nothing)
    cv2.createTrackbar('V low maroon','red',v_low_maroon_init,255,nothing)

    while(1):
                
        # get current positions of six trackbars
        h_low_red = cv2.getTrackbarPos('H low red','red')
        h_high_red = cv2.getTrackbarPos('H high red','red')
        s_low_red = cv2.getTrackbarPos('S low red','red')
        v_low_red = cv2.getTrackbarPos('V low red','red')

        h_low_maroon = cv2.getTrackbarPos('H low maroon','red')
        h_high_maroon = cv2.getTrackbarPos('H high maroon','red')
        s_low_maroon = cv2.getTrackbarPos('S low maroon','red')
        v_low_maroon = cv2.getTrackbarPos('V low maroon','red')

        frame = c.get_frame()
        blur = cv2.GaussianBlur(frame,(11,11), 0)
        hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
        # create masks
        red_mask = cv2.inRange(hsv, (h_low_red, s_low_red, v_low_red), (h_high_red, 255, 255))
        maroon_mask = cv2.inRange(hsv, (h_low_maroon, s_low_maroon, v_low_maroon), (h_high_maroon, 255, 255))
        mask = cv2.bitwise_or(red_mask, maroon_mask)

        cv2.imshow('red', denoiseMask(mask))
        cv2.imshow('actual feed', frame)
                    
        calibrated_thresholds['red'] = {'min': np.array([h_low_red, s_low_red, v_low_red]), 'max': np.array([h_high_red, 255, 255]) }
        calibrated_thresholds['maroon'] = {'min': np.array([h_low_maroon, s_low_maroon, v_low_maroon]),'max': np.array([h_high_maroon, 255, 255]) }

        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break 

    cv2.destroyAllWindows()
    c.close()
    return calibrated_thresholds

if __name__ == "__main__":
    args = parseArgs()
    pitch = int(args.p)
    test = int(args.t)
    data = calibrateThresholds(pitch, test)
    print data
    save_colors(data)
    print "---CALIBRATION DONE------"
