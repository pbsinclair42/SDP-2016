import cv2
import numpy as np

properties={'POS_MSEC' : 0, 
    'POS_FRAMES' : 1,
    'FRAME_WIDTH' : 3, 
    'FRAME_HEIGHT' : 4, 
    'PROP_FPS' : 5,      
    'PROP_MODE' : 9, 
    'BRIGHTNESS' : 10,  
    'CONTRAST' : 11,
    'COLOR' : 12, 
    'HUE' : 13
}

class Camera(object):
    """
    Camera access wrapper.
    """

    def __init__(self, port=0, pitch=0):
        self.capture = cv2.VideoCapture(port)
        self.capture.set(properties['BRIGHTNESS'], 0.45)
        self.capture.set(properties['CONTRAST'], 0.45)
        self.capture.set(properties['COLOR'], 0.5)
        self.capture.set(properties['HUE'], 0.5)

    def get_frame(self, radial_dist=0):
        """
        Retrieve a frame from the camera.

        Returns the frame if available, otherwise returns None.
        """
        status, frame = self.capture.read()
        return frame


    def close(self):
        self.capture.release()
