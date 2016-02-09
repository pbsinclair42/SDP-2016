from math import pi
from os.path import abspath
# root directory:
ROOT_DIR = abspath('constants.py')[:abspath('constants.py').index('SDP')]+'SDP/'
# the number of seconds between updating the robot position
TICK_TIME = 0.1
# our robot's max speed (units per tick)
MAX_SPEED = 1
# the maximum distance from the centre of our robot that we can grab the ball from (units)
GRAB_DISTANCE = 3
# the pitch dimentions in centimeters
PITCH_LENGTH = 300
PITCH_WIDTH = 220
GOAL_WIDTH = 60
BOX_WIDTH = 125
BOX_LENGTH = 75
# the number of pixels per centimeter in the x (length) direction
X_RATIO = 640/300.0
# the number of pixels per centimeter in the y (width) direction
Y_RATIO = 480/220.0
