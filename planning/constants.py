from os.path import abspath
# root directory
ROOT_DIR = abspath('constants.py')[:abspath('constants.py').index('SDP')]+'SDP-2016/'
# the number of seconds between updating the robot position
TICK_TIME = 0.1
# our robot's max speed (cm per second)
MAX_SPEED = 25.0
# our robot's rotational speed (degrees per second)
MAX_ROT_SPEED = 170.0
# the time taken for the robot to grab (seconds)
GRAB_TIME = 0.7
# the time taken for the robot to ungrab (seconds)
UNGRAB_TIME = 0.7
# the time taken from starting kicking to the ball moving (seconds)
BALL_KICK_TIME = 0.3
# the time taken for the robot to kick and unkick
KICK_TIME = 1.0
# the time taken for the robot to ungrab, kick, unkick, and grab (seconds)
FULL_KICK_TIME = GRAB_TIME+KICK_TIME+UNGRAB_TIME
# the ideal distance from the edge of our robot that we should grab the ball from (centimeters)
GRAB_DISTANCE = 5.0
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
POINT_ACCURACY = 10
# how close to a target angle you need to be to count as equal, give or take normal vision inaccuracy (degrees)
ANGLE_ACCURACY = 5
# how close to a target point you need to be to count as 'close enough' for the sake of doing stuff (centimeters)
ITLL_DO_POINT = 5
# how close to a target angle you need to be to count as 'close enough' for the sake of doing stuff (degrees)
ITLL_DO_ANGLE = 5
