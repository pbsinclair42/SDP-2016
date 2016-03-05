import cv2
import numpy as np
from calibrate import *

class Camera(object):
    """
    Camera access wrapper.
    """

    def __init__(self, pitch=0, port=0):
        self.capture = cv2.VideoCapture(port)         
        self.pitch = pitch    

    def get_frame(self, radial_dist=0):
        """
        Retrieve a frame from the camera.

        Returns the frame if available, otherwise returns None.
        """
        status, frame = self.capture.read()
        #frame = cv2.imread('pitch.png')
        frame = step(frame, self.pitch)
        return frame

    def get_frame_hack(self, radial_dist=0):
        """
        Retrieve a frame from the camera.

        Returns the frame if available, otherwise returns None.
        """
        frame = self.get_frame()
        frame = self.get_frame()
        frame = self.get_frame()
        frame = self.get_frame()
        frame = self.get_frame()
        frame = self.get_frame()
        frame = self.get_frame()
        frame = self.get_frame()
        frame = self.get_frame()
        frame = self.get_frame()
        return frame

    def close(self):
        self.capture.release()
