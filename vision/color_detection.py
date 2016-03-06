import sys
from camera import Camera
from calibrate import step
import math
from matplotlib import pyplot as plt
import numpy as np
import cv2
from tools import *
from socket import gethostname

color_range = get_colors()

def nothing(x):
    pass
def denoiseMask(mask):
    kernel =  cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    po = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    po = cv2.morphologyEx(po, cv2.MORPH_OPEN, kernel)
    return po

c = Camera()
num_of_pink_dots = 0
while(1):

    frame = c.get_frame()

    blur = cv2.GaussianBlur(frame,(11,11), 0)

    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    yellow_mask = cv2.inRange(hsv, color_range['yellow']['min'], color_range['yellow']['max'])
    pink_mask = cv2.inRange(hsv, color_range['pink']['min'], color_range['pink']['max'])
    green_mask = cv2.inRange(hsv, color_range['green']['min'], color_range['green']['max'])
    cyan_mask = cv2.inRange(hsv, color_range['bright_blue']['min'], color_range['bright_blue']['max'])
    blue_mask = cv2.inRange(hsv, color_range['blue']['min'], color_range['blue']['max'])
    red_mask = cv2.inRange(hsv, color_range['red']['min'], color_range['red']['max'])
    maroon_mask = cv2.inRange(hsv, color_range['maroon']['min'], color_range['maroon']['max'])
    red = cv2.bitwise_or(red_mask, maroon_mask)
    haha = cv2.bitwise_or(green_mask, cyan_mask)

    cv2.imshow('red', denoiseMask(red))
    cv2.imshow('pink_mask', denoiseMask(pink_mask))
    cv2.imshow('green_mask', denoiseMask(green_mask))
    cv2.imshow('pink_mask', denoiseMask(pink_mask))
    cv2.imshow('cyan_mask', denoiseMask(cyan_mask))
    cv2.imshow('blue_mask', denoiseMask(blue_mask))
    cv2.imshow('yellow_mask', denoiseMask(yellow_mask))

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

    cv2.imshow('frame',frame)


    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

c.close()
cv2.destroyAllWindows()
