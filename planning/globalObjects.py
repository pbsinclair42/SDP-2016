from moveables import Robot, Ball
from helperClasses import Point
from constants import PITCH_WIDTH, GOAL_WIDTH, PITCH_LENGTH, OUR_GOAL

# our supreme robot
me = Robot(name="me")
me.grabbed=True
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
leftGoalCenter = Point(30,PITCH_WIDTH/2)
rightGoalCenter=Point(PITCH_LENGTH-30,PITCH_WIDTH/2)

if OUR_GOAL=='right':
    ourGoal = rightGoalCenter
    opponentGoal = leftGoalCenter
else:
    ourGoal = leftGoalCenter
    opponentGoal = rightGoalCenter


def lineOfSight(From,To):
    dxc = From.x - To.x
    dyc = From.y - To.y

    for obj in moveables:
        dxl = obj.currentPoint.x - To.x
        dyl = obj.currentPoint.y - To.y
        cross = dxc * dyl - dyc * dxl
        if(cross == 0):
            return True
    return False
