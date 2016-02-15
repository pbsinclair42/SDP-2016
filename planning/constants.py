from os.path import abspath
# root directory
ROOT_DIR = abspath('constants.py')[:abspath('constants.py').index('SDP')]+'SDP/'
# the number of seconds between updating the robot position
TICK_TIME = 1
# our robot's max speed (cm per tick)
MAX_SPEED = 50
# the ideal distance from the edge of our robot that we should grab the ball from (centimeters)
GRAB_DISTANCE = 5
# the ideal distance from the edge of our robot that we should open our claws to then grab the ball from (centimeters)
UNGRAB_DISTANCE = 20
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
# how close to a target point you need to be to count as equal, give or take normal vision inaccuracy (centimeters)
POINT_ACCURACY = 1
# how close to a target angle you need to be to count as equal, give or take normal vision inaccuracy (degrees)
ANGLE_ACCURACY = 20
# how close to a target point you need to be to count as 'close enough' for the sake of doing stuff (centimeters)
ITLL_DO_POINT = 10
# how close to a target angle you need to be to count as 'close enough' for the sake of doing stuff (degrees)
ITLL_DO_ANGLE = 10
