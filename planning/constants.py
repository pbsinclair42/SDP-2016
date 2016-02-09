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