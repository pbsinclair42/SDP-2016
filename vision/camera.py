import cv2
import numpy as np
from calibrate_frame import *
from socket import gethostname

class Camera(object):
    """
    Camera access wrapper.
    """


    def __init__(self, pitch=0, port=0, test = 0):
        self.capture = cv2.VideoCapture(port)
        self.pitch = pitch
        self.test = test

    def get_frame(self, radial_dist=0):
        """
        Retrieve a frame from the camera.

        Returns the frame if available, otherwise returns None.
        """
        
        if self.test == 0:
            status, frame = self.capture.read()
            frame = step(frame, self.pitch)
        elif self.test == 1:
            frame = cv2.imread('pitch0.png')

        return frame

    def close(self):
        self.capture.release()
