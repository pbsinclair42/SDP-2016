from helperClasses import Point, BallStatus
import sys
import os
from constants import ROOT_DIR, X_RATIO, Y_RATIO
from cv2 import error as cv2Error
from simulator import simulatedMe, simulatedAlly, simulatedEnemies, simulatedBall

# enable access to the vision package
sys.path.append(ROOT_DIR+'vision')
from tracker import BallTracker, RobotTracker
from camera import Camera
from globalObjects import *

camera = Camera()

# NOTE: UNKNOWN ERROR: Each call of camera.get_frame_hack() is exactly 5 calls behind the actual value!

# check if the camera is connected
try:
    frame = camera.get_frame_hack()
except cv2Error:
    # if you can't get a frame from the camera, warn the user, but continue
    print
    print("********************************")
    print("WARNING: No connection to camera")
    print("********************************")
    print
    camera=None

# if we managed to connect to the camera, set up the robot variables
if camera!=None:
    with open('conf.txt','r') as f:
            context = f.readlines()
            our_team_color = context[0].strip('\n')
            num_of_pink = context[1].strip('\n')
            ball_color = context[2].strip('\n')
            if context[3] == "right":
                ourGoal = Point(PITCH_LENGTH,PITCH_WIDTH/2)
                opponentGoal =  Point(0,PITCH_WIDTH/2)
            else:
                ourGoal = Point(0,PITCH_WIDTH/2)
                opponentGoal = Point(PITCH_LENGTH,PITCH_WIDTH/2)
    #else:
    #print "\nPossible team colors: yellow/light_blue\n"
    #our_team_color = raw_input("Please specify your team colour: ")
    #num_of_pink = raw_input("Please now specify the number of pink dots on your robot: ")
    #ball_color = raw_input("Specify ball color (red/blue): ")
    #if raw_input("Which goal is ours?:") == "right":
    #    ourGoal = Point(PITCH_LENGTH,PITCH_WIDTH/2)
    #    opponentGoal = Point(0,PITCH_WIDTH/2)
    #else:
    #    opponentGoal = Point(PITCH_LENGTH,PITCH_WIDTH/2)
    #    ourGoal = Point(0,PITCH_WIDTH/2)

    #create our trackers:
    robotTracker = RobotTracker(our_team_color, int(num_of_pink))
    ball = BallTracker(ball_color)

    colors = {  'yellow': (0,255,255),
                'light_blue': (255,255,0),
                'pink': (127,0,255),
                'green': (0,255,0),
                'red': (0,0,255),
                'blue': (255,0,0)
             }

    # convert string colors into GBR
    our_circle_color = colors[our_team_color]
    if our_team_color == 'yellow':
        opponent_circle_color = colors['light_blue']
    else :
        opponent_circle_color = colors['yellow']

    # assign colors and names to the robots
    if int(num_of_pink) == 1:
        our_letters = 'GREEN'
        our_col = colors['green']
        our_robot_color = 'green_robot'
        mate_letters = 'PINK'
        mate_col = colors['pink']
        our_mate_color = 'pink_robot'
    else:
        our_letters = 'PINK'
        our_col = colors['pink']
        our_robot_color = 'pink_robot'
        mate_letters = 'GREEN'
        mate_col = colors['green']
        our_mate_color = 'green_robot'


def getBallCoords(frame=None):
    """Returns the position of the ball relative to the pitch, in cm"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame_hack()
        # get the coordinates of the ball
        ball_center = ball.getBallCoordinates(frame)
        # if you couldn't find it, return None
        if ball_center == None:
            return None
        return Point(ball_center[0]*X_RATIO,ball_center[1]*Y_RATIO)
    else:
        # if we have no connection to the camera, just return data from the simulator
        return simulatedBall.currentPoint


def getBallStatus(frame=None):
    """Returns which robot, if any, is holding the ball"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame_hack()
        # TODO: work out the ball status and return it
        return BallStatus.free
    else:
        # if we have no connection to the camera, just return data from the simulator
        # TODO
        return BallStatus.free


def getMyCoords(frame=None):
    """Returns the position of our robot relative to the pitch, in cm"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame_hack()
        # get the info from the frame
        pixelCoordinates = robotTracker.getRobotCoordinates(frame,'us',our_robot_color)
        # if you couldn't find us, return None
        if pixelCoordinates==None:
            return None
        return Point(pixelCoordinates[0]*X_RATIO,pixelCoordinates[1]*Y_RATIO)
    else:
        # if we have no connection to the camera, just return data from the simulator
        return simulatedMe.currentPoint


def getAllyCoords(frame=None):
    """Returns the position of our teammate relative to the pitch, in cm"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame_hack()
        # get the info from the frame
        pixelCoordinates = robotTracker.getRobotCoordinates(frame,'us',our_mate_color)
        # if you couldn't find the ally, return None
        if pixelCoordinates==None:
            return None
        return Point(pixelCoordinates[0]*X_RATIO,pixelCoordinates[1]*Y_RATIO)
    else:
        # if we have no connection to the camera, just return data from the simulator
        return simulatedAlly.currentPoint


def getEnemyCoords(frame=None):
    """Returns the positions of the two enemy robots relative to the pitch, in cm

    Note that the pink robot is enemy A and the green robot is enemy B
    """
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame_hack()
        # get the info from the frame
        pinkPixelCoordinates = robotTracker.getRobotCoordinates(frame,'opponent','pink_robot')
        greenPixelCoordinates = robotTracker.getRobotCoordinates(frame,'opponent','green_robot')
        # if you couldn't find the pink enemy, return None for him
        if pinkPixelCoordinates==None:
            pinkPoint=None
        else:
            pinkPoint = Point(pinkPixelCoordinates[0]*X_RATIO,pinkPixelCoordinates[1]*Y_RATIO)
        # if you couldn't find the green enemy, return None for him
        if greenPixelCoordinates==None:
            greenPoint=None
        else:
            greenPoint = Point(greenPixelCoordinates[0]*X_RATIO,greenPixelCoordinates[1]*Y_RATIO)
        return[pinkPoint,greenPoint]
    else:
        # if we have no connection to the camera, just return data from the simulator
        return [simulatedEnemies[0].currentPoint, simulatedEnemies[1].currentPoint]


def getMyRotation(frame=None):
    """Returns the rotation of our robot in degrees between -180 and 180"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame_hack()
        # get the info from the frame
        rotation = robotTracker.getRobotOrientation(frame, 'us', our_robot_color)[0]
        # if you couldn't find the rotation, return None
        if rotation==None:
            return None
        return rotation[0]
    else:
        # if we have no connection to the camera, just return data from the simulator
        return simulatedMe.currentRotation


def getAllyRotation(frame=None):
    """Returns the rotation of our teammate in degrees between -180 and 180"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame_hack()
        # get the info from the frame
        rotation = robotTracker.getRobotOrientation(frame, 'us', our_mate_color)[0]
        # if you couldn't find the rotation, return None
        if rotation==None:
            return None
        return rotation[0]
    else:
        # if we have no connection to the camera, just return data from the simulator
        return simulatedAlly.currentRotation


def getEnemyRotation(frame=None):
    """Returns the rotation of the two enemy robots in degrees between -180 and 180

    Note that the pink robot is enemy A and the green robot is enemy B
    """
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame_hack()
        # get the info from the frame
        pinkRotation = robotTracker.getRobotOrientation(frame, 'opponent', 'pink_robot')[0]
        greenRotation = robotTracker.getRobotOrientation(frame, 'opponent', 'green_robot')[0]
        if pinkRotation!=None:
            pinkRotation = pinkRotation[0]
        if greenRotation!=None:
            greenRotation = greenRotation[0]
        return [pinkRotation,greenRotation]
    else:
        # if we have no connection to the camera, just return data from the simulator
        return [simulatedEnemies[0].currentRotation, simulatedEnemies[1].currentRotation]


def getAllRobotCoords(frame=None):
    """Returns an array of the position of all the robots"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame_hack()
    return [getMyCoords(frame), getAllyCoords(frame)]+getEnemyCoords(frame)


def getAllRobotRotations(frame=None):
    """Returns an array of the rotation of all the robots"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame_hack()
    return [getMyRotation(frame), getAllyRotation(frame)]+getEnemyRotation(frame)


def getAllRobotDetails(frame=None):
    """Returns an array of tuples of the position and rotation of all the robots"""
    # if we have a connection to the camera...
    if camera!=None:
        # get the current frame if it's not been inputted
        if frame is None:
            frame = camera.get_frame_hack()
        # get the info from the frame
        ourRotation , ourCoords = robotTracker.getRobotOrientation(frame, 'us', our_robot_color)
        allyRotation , allyCoords = robotTracker.getRobotOrientation(frame, 'us', our_mate_color)
        pinkRotation , pinkCoords = robotTracker.getRobotOrientation(frame, 'opponent', 'pink_robot')
        greenRotation , greenCoords = robotTracker.getRobotOrientation(frame, 'opponent', 'green_robot')

        if ourRotation!=None:
            ourRotation = ourRotation[0]
        if allyRotation!=None:
            allyRotation = allyRotation[0]
        if pinkRotation!=None:
            pinkRotation = pinkRotation[0]
        if greenRotation!=None:
            greenRotation = greenRotation[0]

        if ourCoords==None:
            ourPoint=None
        else:
            ourCoords = robotTracker.transformCoordstoCV(ourCoords)
            ourPoint = Point(ourCoords[0]*X_RATIO,ourCoords[1]*Y_RATIO)
        if allyCoords==None:
            allyPoint=None
        else:
            allyCoords = robotTracker.transformCoordstoCV(allyCoords)
            allyPoint = Point(allyCoords[0]*X_RATIO,allyCoords[1]*Y_RATIO)
        if pinkCoords==None:
            pinkPoint=None
        else:
            pinkCoords = robotTracker.transformCoordstoCV(pinkCoords)
            pinkPoint = Point(pinkCoords[0]*X_RATIO,pinkCoords[1]*Y_RATIO)
        if greenCoords==None:
            greenPoint=None
        else:
            greenCoords = robotTracker.transformCoordstoCV(greenCoords)
            greenPoint = Point(greenCoords[0]*X_RATIO,greenCoords[1]*Y_RATIO)
        return [(ourPoint,ourRotation),(allyPoint,allyRotation),(pinkPoint,pinkRotation),(greenPoint,greenRotation)]
    # if we have no connection to the camera, just return data from the simulator
    return zip(getAllRobotCoords(frame), getAllRobotRotations(frame))
