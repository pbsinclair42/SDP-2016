#!/usr/bin/env python2.7
import numpy as np
import cv2
import glob
import json
from copy import copy
import os

class Configure():
    def __init__(self):
        self.objpoints = []
        self.imgpoints = []
        self.height = 480
        self.width = 640

    def getCalibrationParameters(self):
        dim = (8,5)
        objp = np.zeros((dim[0]*dim[1], 3), np.float32)
        objp[:,:2] = np.mgrid[0:dim[0], 0:dim[1]].T.reshape(-1,2)
        images = glob.glob('../samples/pitch1/*.png')

        for fname in images:
            img = cv2.imread(fname)
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, dim, None)
            #cv2.imshow('chess_board_corners', corners)
            #cv2.waitkey(5)
            # If found, add object points, image points (after refining them)
            if ret == True:
                self.objpoints.append(objp)
                corners2 = copy(corners)
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                _ = cv2.cornerSubPix(gray,corners2,(11,11),(-1,-1),criteria)
                self.imgpoints.append(corners2)

                # Draw and display the corners
                # Comment this out to skip showing sample images!
                _ = cv2.drawChessboardCorners(img, dim, corners2, ret)
                cv2.imshow('img',img)
            cv2.waitKey(1000)

        ret, camera_matrix, dist, _, _ = cv2.calibrateCamera(self.objpoints, self.imgpoints, gray.shape[::-1],None,None)
        new_camera_matrix, roi=cv2.getOptimalNewCameraMatrix(camera_matrix, dist,(self.width,self.height),0,(self.width,self.height))

        pitch1 = {'new_camera_matrix' : new_camera_matrix.tolist(),
            'camera_matrix' : camera_matrix.tolist(),
            'dist' : dist.tolist()}

        pitch0 = {'new_camera_matrix' : new_camera_matrix.tolist(),
            'camera_matrix' : camera_matrix.tolist(),
            'dist' : dist.tolist()}

        data = {0 : pitch0, 1: pitch1}

        return data



if __name__ == "__main__":
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../config/", "undistort_pitch1.json")
    C = Configure()
    data = C.getCalibrationParameters()
    with open(path, 'w') as f:
        f.write(json.dumps(data))
