from moveables import Robot, Ball
from helperClasses import Point
from constants import PITCH_WIDTH, GOAL_WIDTH, PITCH_LENGTH

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
# the point at the center of the goal
# TODO: add both goals and ability to differentiate between them and whatnot
leftGoalCenter = Point(30,PITCH_WIDTH/2)
rightGoalCenter=Point(PITCH_LENGTH-30,PITCH_WIDTH/2)

ourGoal = rightGoalCenter
opponentGoal = leftGoalCenter
