#import sys
import time
import random
#import os
#from constants import ROOT_DIR
#from globalObjects import me
#from simulator import Simulator

# enable access to the comms package
#sys.path.append(ROOT_DIR+'comms')
from CommsThread import CommsThread

commsSystem = CommsThread()
# commsSystem = Simulator()

def turn(x):
    """Rotates the robot x degrees anticlockwise.  Use negative numbers to rotate clockwise.  """
    x = int(x)
    commsSystem.rot_move(x, 0)
#    me.moving=True
#    print(me.lastCommandFinished)
    print("Turning " + str(abs(x)) + " degrees " + ("clockwise" if x <= 0 else "anticlockwise"))

def move(distance, angle):
    """Moves `distance` cm at a direction of `angle` degrees"""
    # TODO: update for holo movement
    # ensure the distance is an appropriate size
    distance = int(distance)
    angle = int(angle)
    commsSystem.rot_move(angle, distance)
#    me.moving=True
#    print(me.lastCommandFinished)
    print("Turning " + str(angle) + " degrees then moving " + str(distance) + "cm")


def kick(distance):
    """Kicks the ball `distance` cm"""
    # ensure the distance is an appropriate size
    distance = int(distance)
    if distance>255 or distance<0:
        print("Max distance is 255cm")
        distance=0 if distance<0 else 255
#    commsSystem.kick(distance)
#    me.moving=True ###why ?!
    print("Kicking ball "+str(distance)+"cm")


def grab():
    """Attempts to grab the ball"""
    commsSystem.grab()
#    me.moving=True
    print("Grabbing ball")

def ungrab():
    """Attempts to ungrab the ball"""
    commsSystem.ungrab()
#    me.moving=True
    print("Opening claw")

def stop():
    """Stops all communications"""
    commsSystem.stop()
    print("Stopping all communications")

def flush():
    """Clears all commands and stops all motors"""
    commsSystem.flush()
    print("Clearing all commands")

if __name__ == "__main__":
    """
        Big test based on random data
    """
    while True:
        if commsSystem.am_i_done():
            
            deg = random.random() * 90
            turn(90)