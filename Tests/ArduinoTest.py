import sys
# import os
from math import *

# from constants import ROOT_DIR
import unittest
from os.path import abspath
# enable access to the comms package
OOT_DIR = abspath('constants.py')[:abspath('constants.py').index('SDP')]+'SDP/'
sys.path.append(ROOT_DIR+'comms')
from RobotCommunications import RobotCommunications

# try to connect to the comms system.
# If unsuccessful, continue simulation nonetheless
try:
    commsSystem = RobotCommunications()
except BaseException:
    print
    print("****************************")
    print("WARNING: Robot not connected")
    print("****************************")
    print
    commsSystem = False


class TestCommsMethods(unittest.TestCase):
    def holo_test(self):
        b = B00000010
        s = commsSystem.holo(90, 0)
        print(s)
        self.assertTrue(b in s)

    def holoneg_test(self):
        pass

    def stop_test(self):
        pass

    def rotate_test(self):
        pass

    def rotateneg_test(self):
        pass
        """Rotates the robot x radians clockwise.
        Use negative numbers to rotate anticlockwise.  """
        x = 0
        if commsSystem:
            commsSystem.rotate(0, 360*x/(2*pi))
        a = (" anticlockwise "if x >= 0 else " clockwise ")
        b = str(abs(x))
        print ("Turning %s radians %s" % (b, a))

    def ungrab_test(self):
        """Moves `distance` cm at a direction of `angle` radians"""
        angle = 90
        distance = 10
        if commsSystem:
            commsSystem.holo(360*angle / (2*pi), distance)
        print("Moving %d cm at an angle of %d  radians" % (distance, angle))

    def kick_test(self):
        pass
        """Kicks the ball `distance` cm"""
        if commsSystem:
            commsSystem.kick(distance)
        print("Kicking ball "+str(distance)+"cm")

    def grab_test(self):
        pass
        """Attempts to grab the ball"""
        if commsSystem:
            commsSystem.grab()
        print("Grabbing ball")

    def flush_test(self):
        pass


if __name__ == '__main__':
        unittest.main()
