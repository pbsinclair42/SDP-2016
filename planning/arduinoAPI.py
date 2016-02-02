import sys
import os
from math import *

# enable access to the comms package
sys.path.append(os.path.dirname(os.path.abspath("constants.py"))[:-8]+'comms')
from RobotCommunications import RobotCommunications

# try to connect to the comms system.  If unsuccessful, continue simulation nonetheless
try:
    commsSystem = RobotCommunications()
except BaseException:
    print("Robot not connected")
    commsSystem = False

def turn(x):
    """Rotates the robot x radians clockwise.  Use negative numbers to rotate anticlockwise.  """
    if commsSystem:
        commsSystem.rotate(0, 360*x/(2*pi))
    print("Turning "+str(abs(x))+"radians "+"clockwise" if x>=0 else "anticlockwise")


def move(distance, angle):
    """Moves `distance` cm at a direction of `angle` radians"""
    if commsSystem:
        commsSystem.holo(360*angle/(2*pi),distance)
    print("Moving "+str(distance)+"cm at an angle of "+str(angle)+" radians")


def kick(distance):
    """Kicks the ball `distance` cm"""
    if commsSystem:
        commsSystem.kick(distance)
    print("Kicking ball "+str(distance)+"cm")


def grab():
    """Attempts to grab the ball"""
    if commsSystem:
        commsSystem.grab()
    print("Grabbing ball")


def stop():
    """Stops all motors"""
    if commsSystem:
        commsSystem.stop()
    print("Stopping all motors")
