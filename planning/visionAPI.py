from helperClasses import Point, BallStatus
import sys
import os
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
    # create our tracker object:
    robotTracker = RobotTracker(our_team_color, int(num_of_pink))

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


"""
    # get robot orientations and centers  
    our_orientation, our_robot_center = robotTracker.getRobotOrientation(frame, 'us', our_robot_color)
    our_mate_orientation, our_mate_center = robotTracker.getRobotOrientation(frame, 'us', our_mate_color)
    pink_opponent_orientation, pink_opponent_center = robotTracker.getRobotOrientation(frame, 'opponent', 'pink_robot')
    green_opponent_orientation, green_opponent_center = robotTracker.getRobotOrientation(frame, 'opponent', 'green_robot')
"""

def getBallCoords(frame=None):
    """Returns the position of the ball relative to the pitch"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame==None:
            frame = camera.get_frame()
    else:
        # if we have no connection to the camera, just return some dummy data
        return Point(15,20)

def getBallStatus(frame=None):
    """Returns which robot, if any, is holding the ball"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame==None:
            frame = camera.get_frame()
    else:
        # if we have no connection to the camera, just return some dummy data
        return BallStatus.free

def getMyCoords(frame=None):
    """Returns the position of our robot relative to the pitch"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame==None:
            frame = camera.get_frame()
        # get the info from the frame
        pixelCoordinates = robotTracker.getRobotCoordinates(frame,'us',our_robot_color)
        cartesianCoordinates = robotTracker.transformCoordstoDecartes(pixelCoordinates)
        return Point(pixelCoordinates[0],pixelCoordinates[1])
    else:
        # if we have no connection to the camera, just return some dummy data
        return Point(40,35)

def getAllyCoords(frame=None):
    """Returns the position of our teammate relative to the pitch"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame==None:
            frame = camera.get_frame()
        # get the info from the frame
        pixelCoordinates = robotTracker.getRobotCoordinates(frame,'us',our_mate_color)
        cartesianCoordinates = robotTracker.transformCoordstoDecartes(pixelCoordinates)
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
        if frame==None:
            frame = camera.get_frame()
        # get the info from the frame
        pinkPixelCoordinates = robotTracker.getRobotCoordinates(frame,'opponent','pink_robot')
        pinkCartesianCoordinates = robotTracker.transformCoordstoDecartes(pinkPixelCoordinates)
        greenPixelCoordinates = robotTracker.getRobotCoordinates(frame,'opponent','green_robot')
        greenCartesianCoordinates = robotTracker.transformCoordstoDecartes(greenPixelCoordinates)
        return[Point(pinkPixelCoordinates[0],pinkPixelCoordinates[1]),Point(greenPixelCoordinates[0],greenPixelCoordinates[1])]
    else:
        # if we have no connection to the camera, just return some dummy data
        return [Point(80,10), Point(220,76)]

def getMyRotation(frame=None):
    """Returns the rotation of our robot in radians between -pi and pi"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame==None:
            frame = camera.get_frame()
    else:
        # if we have no connection to the camera, just return some dummy data
        return 1.2

def getAllyRotation(frame=None):
    """Returns the rotation of our teammate in radians between -pi and pi"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame==None:
            frame = camera.get_frame()
    else:
        # if we have no connection to the camera, just return some dummy data
        return 1.63

def getEnemyRotation(frame=None):
    """Returns the rotation of the two enemy robots in radians between -pi and pi"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame==None:
            frame = camera.get_frame()
    else:
        # if we have no connection to the camera, just return some dummy data
        return [2.1, -0.67]

def getAllRobotCoords(frame=None):
    """Returns an array of the position of all the robots"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame==None:
            frame = camera.get_frame()
    return [getMyCoords(frame), getAllyCoords(frame)]+getEnemyCoords(frame)

def getAllRobotRotations(frame=None):
    """Returns an array of the rotation of all the robots"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame==None:
            frame = camera.get_frame()
    return [getMyRotation(frame), getAllyRotation(frame)]+getEnemyRotation(frame)

def getAllRobotDetails(frame=None):
    """Returns an array of tuples of the position and rotation of all the robots"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame==None:
            frame = camera.get_frame()
    return zip(getAllRobotCoords(frame), getAllRobotRotations(frame))
