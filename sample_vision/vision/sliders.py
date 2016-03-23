# Example code is taken from https://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_gui/py_trackbar/py_trackbar.html#trackbar
# I modified it slightly to use the HSV colorspace instead of RGB - Calum
# It also allowas the user to select the upper and lower bounds of values which represent a given colour in hsv space.

import cv2
import numpy as np

def nothing(x):
    pass

def getColours():

    cv2.startWindowThread()

    colours = ["white", "blue", "bright_blue", "pink", "red", "maroon", "green", "bright_green","yellow"]
    colourvalues = {"white": [[0,0,0],[0,0,0]], "blue": [[0,0,0],[0,0,0]],"bright_blue": [[0,0,0],[0,0,0]],"pink": [[0,0,0],[0,0,0]],"red": [[0,0,0],[0,0,0]],"maroon": [[0,0,0],[0,0,0]],"green": [[0,0,0],[0,0,0]],"bright_green": [[0,0,0],[0,0,0]], "yellow": [[0,0,0],[0,0,0]]}
    # defines the colours and the corresponding ranges of hsv values

    # Create a black image, a window
    img = np.zeros((300,512,3), np.uint8)
    cv2.namedWindow('image')

    # create trackbars for color change
    cv2.createTrackbar('H','image',0,179,nothing)
    cv2.createTrackbar('S','image',0,255,nothing)
    cv2.createTrackbar('V','image',0,255,nothing)

    # create tracker for which colour value we want to set
    # i.e. 1= blue, 2 = red, etc.

    cv2.createTrackbar('Set Value', 'image',0,8,nothing)

    while(1):
        img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        cv2.imshow('image',img)
        k = cv2.waitKey(10) & 0xFF
        if k == 27:
            break
        if k == 97:
            print("Values of [" + str(r) + ", " + str(g) + ", " + str(b) + "] set for lower bound of colour " + colours[valueToSet] + ".")
            colourvalues[colours[valueToSet]][0] = [r,g,b]
        if k == 100:
            print("Values of [" + str(r) + ", " + str(g) + ", " + str(b) + "] set for upper bound of colour " + colours[valueToSet] + ".")
            colourvalues[colours[valueToSet]][1] = [r,g,b]

        # get current positions of four trackbars
        r = cv2.getTrackbarPos('H','image')
        g = cv2.getTrackbarPos('S','image')
        b = cv2.getTrackbarPos('V','image')
        valueToSet = cv2.getTrackbarPos('Set Value', 'image')
        img[:] = [r,g,b]

    cv2.destroyWindow('image')
    cv2.waitKey(1)
    return colourvalues



def getIndividualColour(h,s,v, colourname):

    cv2.startWindowThread()

    # Create a black image, a window
    img = np.zeros((300,512,3), np.uint8)
    cv2.namedWindow('image')

    # create trackbars for color change
    cv2.createTrackbar('H','image',h,179,nothing)
    cv2.createTrackbar('S','image',s,255,nothing)
    cv2.createTrackbar('V','image',v,255,nothing)

    # create tracker for which colour value we want to set
    # i.e. 1= blue, 2 = red, etc.

    while(1):
        img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        cv2.imshow('image',img)
        k = cv2.waitKey(10) & 0xFF
        if k == 27:
            break
        if k == 97:
            print("Returning values of [" + str(r) + ", " + str(g) + ", " + str(b) + "] for colour \"" + colourname + "\".")
        # get current positions of four trackbars
        r = cv2.getTrackbarPos('H','image')
        g = cv2.getTrackbarPos('S','image')
        b = cv2.getTrackbarPos('V','image')
        img[:] = [r,g,b]

    cv2.destroyWindow('image')
    cv2.waitKey(1)
    return [r,g,b]
