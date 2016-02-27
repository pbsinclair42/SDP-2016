import sys
import time
import os
from constants import ROOT_DIR
from globalObjects import me
from simulator import Simulator

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
    commsSystem = Simulator()

def turn(x):
    """Rotates the robot x degrees anticlockwise.  Use negative numbers to rotate clockwise.  """
    x = int(x)
    if x>255 or x< (-255):
        print("Max turn is 255 degrees")
        # set x to 255 times the sign of x
        x=255*x/abs(x)
    instruction_count = commsSystem.current_cmd
    if x<0:
        commsSystem.rotateneg(0, abs(x))
    else:
        commsSystem.rotate(0, abs(x))
    print("Turning "+str(abs(x))+" degrees "+("clockwise" if x<=0 else "anticlockwise"))
    """Wait until the command has finished executing"""
    while instruction_count == commsSystem.current_cmd:
        time.sleep(0.01)

def move(distance, angle):
    """Moves `distance` cm at a direction of `angle` degrees"""
    # TODO: update for holo movement
    # ensure the distance is an appropriate size
    distance = int(distance)
    if distance>255 or distance<0:
        print("Max distance is 255cm")
        distance=0 if distance<0 else 255
    # ensure the angle is an appropriate size
    angle = int(angle)
    if angle>255 or angle< (-255):
        print("Max turn is 255 degrees")
        # set angle to 255 times the sign of angle
        angle=255*angle/abs(angle)
    instruction_count = commsSystem.current_cmd
    if angle>=0:
        commsSystem.rotate(distance, abs(angle))
    elif angle<=0:
        commsSystem.rotateneg(distance, abs(angle))
    print("Moving "+str(distance)+"cm at an angle of "+str(angle)+" degrees")
    """Wait until the command has finished executing"""
    while instruction_count == commsSystem.current_cmd:
        time.sleep(0.01)


def kick(distance):
    """Kicks the ball `distance` cm"""
    # ensure the distance is an appropriate size
    distance = int(distance)
    instruction_count = commsSystem.current_cmd
    if distance>255 or distance<0:
        print("Max distance is 255cm")
        distance=0 if distance<0 else 255
    commsSystem.kick(distance)
    print("Kicking ball "+str(distance)+"cm")
    """Wait until the command has finished executing"""
    while instruction_count == commsSystem.current_cmd:
        time.sleep(0.01)


def grab():
    """Attempts to grab the ball"""
    instruction_count = commsSystem.current_cmd
    commsSystem.grab()
    print("Grabbing ball")
    """Wait until the command has finished executing"""
    while instruction_count == commsSystem.current_cmd:
        time.sleep(0.01)

def ungrab():
    """Attempts to ungrab the ball"""
    instruction_count = commsSystem.current_cmd
    commsSystem.ungrab()
    print("Opening claw")
    """Wait until the command has finished executing"""
    while instruction_count == commsSystem.current_cmd:
        time.sleep(0.01)

def stop():
    """Stops all motors"""
    instruction_count = commsSystem.current_cmd
    commsSystem.stop()
    print("Stopping all motors")
    """Wait until the command has finished executing"""
    while instruction_count == commsSystem.current_cmd:
        time.sleep(0.01)

def flush():
    """Clears all commands and stops all motors"""
    instruction_count = commsSystem.current_cmd
    commsSystem.flush()
    print("Clearing all commands")
    """Wait until the command has finished executing"""
    while instruction_count == commsSystem.current_cmd:
        time.sleep(0.01)
