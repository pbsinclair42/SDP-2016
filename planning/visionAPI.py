from helperClasses import Point, BallStatus
import sys
import os
from math import radians
from constants import ROOT_DIR
from cv2 import error as cv2Error

# enable access to the vision package
sys.path.append(ROOT_DIR+'vision')
from tracker import BallTracker, RobotTracker
from camera import Camera

camera = Camera()

# NOTE: UNKNOWN ERROR: Each call of camera.get_frame() is exactly 5 calls behind the actual value!

# check if the camera is connected
try:
    frame = camera.get_frame()
except cv2Error:
    # if you can't get a frame from the camera, warn the user, but continue
    print
    print("********************************")
    print("WARNING: No connection to camera")
    print("********************************")
    print
    camera=None

# if we managed to connect to the camera, set up the robot
if camera!=None:
    print "\nPossible team colors: yellow/light_blue\n"
    our_team_color = raw_input("Please specify your team colour: ")
    num_of_pink = raw_input("Please now specify the number of pink dots on your robot: ")
    ball_color = raw_input("Specify ball color: ")
    # create our trackers:
    robotTracker = RobotTracker(our_team_color, int(num_of_pink))
    ball = BallTracker(ball_color)

    # convert string colors into GBR
    if our_team_color == 'yellow':
        our_circle_color = (0,255,255)
        opponent_circle_color = (255,255,0)
    else :
        our_circle_color = (255,255,0)
        opponent_circle_color = (0,255,255)

    # assign our robot a color
    if int(num_of_pink) == 1:
        our_letters = 'GREEN'
        our_col = (0,255,0)
        our_robot_color = 'green_robot'
        mate_letters = 'PINK'
        mate_col = (127,0,255)

        our_mate_color = 'pink_robot' 
    else:
        our_letters = 'PINK'
        our_col = (127,0,255)
        our_robot_color = 'pink_robot' 
        mate_letters = 'GREEN' 
        mate_col = (0,255,0)
        our_mate_color = 'green_robot' 


def getBallCoords(frame=None):
    """Returns the position of the ball relative to the pitch"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame()
        # get the coordinates of the ball
        ball_center = ball.getBallCoordinates(frame)
        # if you couldn't find it, return None
        if ball_center == None:
            return None
        return Point(ball_center[0],ball_center[1])
    else:
        # if we have no connection to the camera, just return some dummy data
        return Point(15,20)

def getBallStatus(frame=None):
    """Returns which robot, if any, is holding the ball"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame()
        # TODO: work out the ball status and return it
        return BallStatus.free
    else:
        # if we have no connection to the camera, just return some dummy data
        return BallStatus.free

def getMyCoords(frame=None):
    """Returns the position of our robot relative to the pitch"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame()
        # get the info from the frame
        pixelCoordinates = robotTracker.getRobotCoordinates(frame,'us',our_robot_color)
        # if you couldn't find us, return None
        if pixelCoordinates==None:
            return None
        return Point(pixelCoordinates[0],pixelCoordinates[1])
    else:
        # if we have no connection to the camera, just return some dummy data
        return Point(40,35)

def getAllyCoords(frame=None):
    """Returns the position of our teammate relative to the pitch"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame()
        # get the info from the frame
        pixelCoordinates = robotTracker.getRobotCoordinates(frame,'us',our_mate_color)
        # if you couldn't find the ally, return None
        if pixelCoordinates==None:
            return None
        return Point(pixelCoordinates[0],pixelCoordinates[1])
    else:
        # if we have no connection to the camera, just return some dummy data
        return Point(100,155)

def getEnemyCoords(frame=None):
    """Returns the positions of the two enemy robots relative to the pitch

    Note that the pink robot is enemy A and the green robot is enemy B
    """
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame()
        # get the info from the frame
        pinkPixelCoordinates = robotTracker.getRobotCoordinates(frame,'opponent','pink_robot')
        # if you couldn't find the pink enemy, return None for him
        if pinkPixelCoordinates==None:
            pinkPoint=None
        else:
            pinkPoint = Point(pinkPixelCoordinates[0],pinkPixelCoordinates[1])
        greenPixelCoordinates = robotTracker.getRobotCoordinates(frame,'opponent','green_robot')
        # if you couldn't find the green enemy, return None for him
        if greenPixelCoordinates==None:
            greenPoint=None
        else:
            greenPoint = Point(greenPixelCoordinates[0],greenPixelCoordinates[1])
        return[pinkPoint,greenPoint]
    else:
        # if we have no connection to the camera, just return some dummy data
        return [Point(80,10), Point(220,76)]

def getMyRotation(frame=None):
    """Returns the rotation of our robot in radians between -pi and pi"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame()
        # get the info from the frame
        rotation = robotTracker.getRobotOrientation(frame, 'us', our_robot_color)[0]
        # if you couldn't find the rotation, return None
        if rotation==None:
            return None
        return radians(rotation[0])
    else:
        # if we have no connection to the camera, just return some dummy data
        return 1.2

def getAllyRotation(frame=None):
    """Returns the rotation of our teammate in radians between -pi and pi"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame()
        # get the info from the frame
        rotation = robotTracker.getRobotOrientation(frame, 'us', our_mate_color)[0]
        # if you couldn't find the rotation, return None
        if rotation==None:
            return None
        return radians(rotation[0])
    else:
        # if we have no connection to the camera, just return some dummy data
        return 1.63

def getEnemyRotation(frame=None):
    """Returns the rotation of the two enemy robots in radians between -pi and pi"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame()
        # get the info from the frame
        pinkRotation = robotTracker.getRobotOrientation(frame, 'opponent', 'pink_robot')[0]
        greenRotation = robotTracker.getRobotOrientation(frame, 'opponent', 'green_robot')[0]
        if pinkRotation!=None:
            pinkRotation = radians(pinkRotation[0])
        if greenRotation!=None:
            greenRotation = radians(greenRotation[0])
        return [pinkRotation,greenRotation]
    else:
        # if we have no connection to the camera, just return some dummy data
        return [2.1, -0.67]

def getAllRobotCoords(frame=None):
    """Returns an array of the position of all the robots"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame()
    return [getMyCoords(frame), getAllyCoords(frame)]+getEnemyCoords(frame)

def getAllRobotRotations(frame=None):
    """Returns an array of the rotation of all the robots"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame()
    return [getMyRotation(frame), getAllyRotation(frame)]+getEnemyRotation(frame)

def getAllRobotDetails(frame=None):
    """Returns an array of tuples of the position and rotation of all the robots"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame()
    return zip(getAllRobotCoords(frame), getAllRobotRotations(frame))
