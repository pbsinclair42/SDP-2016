import sys
# import os
from math import *

# from constants import ROOT_DIR
import unittest
from os.path import abspath
# enable access to the comms package
ROOT_DIR = abspath('constants.py')[:abspath('constants.py').index('SDP')]+'SDP/'
sys.path.append(ROOT_DIR+'comms')
sys.path.append(ROOT_DIR+'planning')
from RobotCommunications import RobotCommunications
import simulator

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
    commsSystem = simulator.Simulator()


class TestCommsMethods(unittest.TestCase):
    def test(self):
        b = "B00000010"
        s = commsSystem.holo(90, 0)
        print(s)
        self.assertTrue(b in s)

    def test_holoneg(self):
        pass

    def test_stop(self):
        pass

    def test_rotate(self):
        pass

    def test_rotateneg(self):
        pass
        """Rotates the robot x radians clockwise.
        Use negative numbers to rotate anticlockwise.  """
        x = 0
        if commsSystem:
            commsSystem.rotate(0, 360*x/(2*pi))
        a = (" anticlockwise "if x >= 0 else " clockwise ")
        b = str(abs(x))
        print ("Turning %s radians %s" % (b, a))

    def test_ungrab(self):
        """Moves `distance` cm at a direction of `angle` radians"""
        angle = 90
        distance = 10
        if commsSystem:
            commsSystem.holo(360*angle / (2*pi), distance)
        print("Moving %d cm at an angle of %d  radians" % (distance, angle))

    def test_kick(self):
        pass
        distance = 0
        """Kicks the ball `distance` cm"""
        if commsSystem:
            commsSystem.kick(distance)
        else:
            return
        print("Kicking ball "+str(distance)+"cm")

    def test_grab(self):
        pass
        """Attempts to grab the ball"""
        if commsSystem:
            commsSystem.grab()
        print("Grabbing ball")

    def test_flush(self):
        pass


if __name__ == '__main__':
        unittest.main()
