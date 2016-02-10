from math import pi
from os.path import abspath
# root directory:
ROOT_DIR = abspath('constants.py')[:abspath('constants.py').index('SDP')]+'SDP/'
# the number of seconds between updating the robot position
TICK_TIME = 0.1
# our robot's max speed (cm per tick)
MAX_SPEED = 1
# the maximum distance from the centre of our robot that we can grab the ball from (centimeters)
GRAB_DISTANCE = 3
# the number of centimeters per pixel in the x (length) direction
X_RATIO = 300.0/640
# the number of centimeters per pixel in the y (width) direction
Y_RATIO = 220.0/480
# the pitch dimentions in centimeters
PITCH_LENGTH = 300
PITCH_WIDTH = 220
GOAL_WIDTH = 60
BOX_WIDTH = 125
BOX_LENGTH = 75
# the item dimentions in centimeters
BALL_DIAMETER = 4.9
BALL_RADIUS = BALL_DIAMETER/2.0
ROBOT_WIDTH = 20
