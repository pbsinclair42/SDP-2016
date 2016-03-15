from os.path import abspath
# root directory
ROOT_DIR = abspath('constants.py')[:abspath('constants.py').index('SDP')]+'SDP-2016/'
# the number of seconds between updating the robot position
TICK_TIME = 0.9
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
GRAB_DISTANCE = 6.0
# the ideal distance from the edge of our robot that we should open our claws to then grab the ball from (centimeters)
UNGRAB_DISTANCE = 20.0
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
ROBOT_WIDTH = 6

# the distance from the ball that a robot needs to be before we assume it's got it (centimeters)
BALL_OWNERSHIP_DISTANCE = 20

# how close to a target point you need to be to count as equal, give or take normal vision inaccuracy (centimeters)
POINT_ACCURACY = 3
# how close to a target angle you need to be to count as equal, give or take normal vision inaccuracy (degrees)
ANGLE_ACCURACY = 15
# how close to a target point you need to be to count as 'close enough' for the sake of doing stuff (centimeters)
ITLL_DO_POINT = 5
# how close to a target angle you need to be to count as 'close enough' for the sake of doing stuff (degrees)
ITLL_DO_ANGLE = 15


# initialize the variables with dummy values that will be replaced with info from conf.txt
TEAM_COLOUR = 'yellow'
OUR_COLOUR = 'green'
BALL_COLOUR = 'red'
OUR_GOAL = 'left'
USING_SIMULATOR = False

# get the information from the config file
with open('conf.txt','r') as f:

    class _ConfigError(Exception):
        """Simple exception for config errors"""
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr(self.value)

    config = f.readlines()
    # get team colour
    TEAM_COLOUR = config[0].lower().strip()
    if TEAM_COLOUR != 'yellow' and TEAM_COLOUR != 'bright_blue':
        raise _ConfigError("Invalid team colour")
    # get our robot colour
    OUR_COLOUR = config[1].lower().strip()
    if OUR_COLOUR != 'pink' and OUR_COLOUR != 'green':
        raise _ConfigError("Invalid robot colour")
    # get ball colour
    BALL_COLOUR = config[2].lower().strip()
    if BALL_COLOUR!='red' and BALL_COLOUR!='blue':
        raise _ConfigError("Invalid ball colour")
    # get our goal side
    OUR_GOAL = config[3].lower().strip()
    if OUR_GOAL!='left' and OUR_GOAL!='right':
        raise _ConfigError("Invalid side for our goal")
    # get if using simulator
    if config[4].lower().strip() == 'true':
        USING_SIMULATOR=True
    elif config[4].lower().strip() != 'false':
        raise _ConfigError("Invalid value for if using simulator")





