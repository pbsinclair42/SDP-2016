import sys
import os
from math import *
from constants import ROOT_DIR
from globalObjects import me

# enable access to the comms package
sys.path.append(ROOT_DIR+'comms')
from RobotCommunications import RobotCommunications

# try to connect to the comms system.  If unsuccessful, continue simulation nonetheless
try:
    commsSystem = RobotCommunications()
except BaseException:
    print
    print("****************************")
    print("WARNING: Robot not connected")
    print("****************************")
    print
    commsSystem = False

def turn(x):
    """Rotates the robot x radians anticlockwise.  Use negative numbers to rotate clockwise.  """
    x = int(degrees(x))
    if commsSystem:
        if (x>255 or x< (-255)):
            print("Max turn is 255 degrees")
            # set x to 255 times the sign of x
            x=255*x/abs(x)
        if (x>=0):
            commsSystem.rotateneg(0, abs(x))
        elif (x<=0):
            commsSystem.rotate(0, abs(x))
    print("Turning "+str(abs(x))+"degrees "+("clockwise" if x<=0 else "anticlockwise"))


def move(distance, angle):
    """Moves `distance` cm at a direction of `angle` radians"""
    # TODO: update for holo movement
    if commsSystem:
        commsSystem.rotate(distance,angle)
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


def ungrab():
    """Attempts to grab the ball"""
    if commsSystem:
        commsSystem.ungrab()
    print("Grabbing ball")


def stop():
    """Stops all motors"""
    if commsSystem:
        commsSystem.stop()
    me.moving=False
    me.rotationHistory=[]
    print("Stopping all motors")


def flush():
    """Clears all commands and stops all motors"""
    if commsSystem:
        commsSystem.flush()
    me.moving=False
    me.rotationHistory=[]
    print("Clearing all commands")
