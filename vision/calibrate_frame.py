#!/usr/bin/env python2.7
#sys.path.insert(0, '../')
#sys.path.insert(0, './')
import numpy as np
import cv2
import sys
import os
from tools import *
#from functools import partial
from os.path import abspath


COLS = 640
ROWS = 480
PATH = os.path.dirname(os.path.realpath(__file__))
# enable access to the json file from any directory in SDP
absPathToJson = PATH+'/config/undistort.json'

pitches = read_json(absPathToJson)


def step(frame, pitch=0):
    frame = undistort(frame, pitch)
    frame = perspective(frame, pitch)
    frame = translate(frame, pitch)
    frame = warp(frame, pitch)
    return frame

def pitch_to_numpy(pitch=0):
    ret = {}
    for key, value in pitch.iteritems():
        ret[key] = np.asarray(value)
    return ret


''' Scale center '''
def translate(frame, pitch=0):
    if pitch == 0:
        #M = np.float32([[1,0,-5],[0,1,-5]])
        #return cv2.warpAffine(frame, M, (640,480))
        return frame
    else: 
        return frame      

def undistort(frame, pitch_num=0):
    pitch = pitch_to_numpy(pitches[str(pitch_num)])

    return cv2.undistort(frame, pitch["camera_matrix"], pitch["dist"], None,
                         pitch["new_camera_matrix"])


''' Rotate frame '''
def warp(frame,pitch=0):
    if pitch == 0: 
        M = cv2.getRotationMatrix2D((COLS/2, ROWS/2), 1, 1)
        return cv2.warpAffine(frame, M, (COLS, ROWS))
    else:
        M = cv2.getRotationMatrix2D((COLS/2, ROWS/2), 0, 1)
        return cv2.warpAffine(frame, M, (COLS, ROWS))

''' Apply perspective transformation '''
def perspective(frame, pitch=0):
    if pitch == 0:
        pts1 = np.float32([[0,0],[13,478],[COLS,ROWS],[COLS,0]])
        pts2 = np.float32([[0,0],[0,ROWS],[COLS,ROWS],[COLS,0]])
        M = cv2.getPerspectiveTransform(pts1,pts2)
        dst = cv2.warpPerspective(frame,M,(COLS,ROWS))
        return dst
    else:
        pts1 = np.float32([[5,5],[5,475],[COLS,ROWS],[COLS,0]])
        pts2 = np.float32([[0,0],[0,ROWS],[COLS,ROWS],[COLS,0]])
        M = cv2.getPerspectiveTransform(pts1,pts2)
        dst = cv2.warpPerspective(frame,M,(COLS,ROWS))
        return dst           

