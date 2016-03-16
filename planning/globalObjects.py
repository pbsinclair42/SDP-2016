from moveables import Robot, Ball
from helperClasses import Point
from constants import PITCH_WIDTH, GOAL_WIDTH, PITCH_LENGTH, OUR_GOAL

# our supreme robot
me = Robot(name="me")
me.lastCommandFinished=-1
# Team 3's robot
ally = Robot(name="ally")
# the two robots we're against
enemies = [Robot(name="pinkEnemy"), Robot(name="greenEnemy")]
# a list containing all robots on the field for convenience
robots = [me, ally]+enemies
# guess what this could possibly be
ball = Ball(name="ball")
#list of all movables
moveables = [me,ally,ball]+enemies

# the point at the center of the goal
leftGoalCenter = Point(15,PITCH_WIDTH/2)
rightGoalCenter=Point(PITCH_LENGTH-15,PITCH_WIDTH/2)

if OUR_GOAL=='right':
    ourGoal = rightGoalCenter
    opponentGoal = leftGoalCenter
else:
    ourGoal = leftGoalCenter
    opponentGoal = rightGoalCenter
