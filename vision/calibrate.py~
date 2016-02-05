#!/usr/bin/env python2.7
import cv2
import util
import numpy as np

class Calibrate():

    COLS = 640
    ROWS = 480

    def __init__(self):
        pass

    def step(self, frame):
        functions = [
            self.perspective,
            self.translate,
            self.undistort,
            self.warp,
            ]

        return util.compose(*functions)(frame)


    def process(self, frame):
        pass


    def pitch_to_numpy(self, pitch):
        ret = {}

        for key, value in pitch.iteritems():
            ret[key] = np.asarray(value)

        return ret

    def translate(self, frame):
        M = cv2.float32([[1,0,3],[0,1,0]])
        return cv2.warpAffine(frame, M, (640,480))

    def undistort(self, frame):
        pitches = util.read_json("config/undistort.json")

        pitch = self.pitch_to_numpy(pitches["0"])

        return cv2.undistort(frame, pitch["camera_matrix"], pitch["dist"], None,
                            pitch["new_camera_matrix"])

    def warp(self, frame):
        M = cv2.getRotationMatrix2D((self.COLS/2, self.ROWS/2), 3, 1)
        return cv2.warpAffine(frame, M, (self.COLS, self.ROWS))

    def perspective(self, frame):

        pts1 = np.float32([[-5,0],[15,476],[609,474],[627,5]])
        pts2 = np.float32([[0,0],[0,475],[640,480],[640,0]])

        M = cv2.getPerspectiveTransform(pts1,pts2)

        dst = cv2.warpPerspective(frame,M,(640,480))

        return dst


    def fun(self):
        self.show_frame(self.step())

    def show_frame(self, frame):
        cv2.imshow("distort", frame)

