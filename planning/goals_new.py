from constants import *
from globalObjects import *
from helperClasses import Point, Goals, Actions
from helperFunctions import sin, cos
import RobotController as controller
import time

"""TODO
Position to receive pass - Speak to Other Team About that
Guard goal
Tell teammate plans (?)
"""


def collectBall():
    """Make `collectBall` the goal of our robot,
    and implement the plan for achieving this"""
    angle_to_face = ball.bearing(Point(0,0))
    angle_to_move = angle_to_face
    distance_to_move = me.distance(ball.currentPoint)
    controller.move(angle_to_face,angle_to_move,distance_to_move,True)


    """me.plan = [{'action': Actions.moveToPoint, 'targetFunction': ungrabHere},
               {'action': Actions.ungrab},
               {'action': Actions.moveToPoint, 'targetFunction': grabHere},
               {'action': Actions.grab}]"""


def shoot():#NEED TO GET THE FUCK OUT OF THERE
    """Make `shoot` the goal of our robot,
    and implement the plan for achieving this"""
    angle_to_face = me.bearing(opponentGoal)#Not 100% convinced on this bearing
    if nearEnough(me.orientation, angle_to_face):
        controller.kick()
    else:
        controller.move(angle_to_face,0,0)


    """me.plan = [{'action': Actions.rotateToAngle, 'targetFunction': aim},
               {'action': Actions.kick, 'targetFunction': distanceToKick}]"""


def passBall():
    angle_to_face = me.bearing(ally)#Not 100% convinced on this bearing
    if nearEnough(me.orientation, angle_to_face):
        controller.kick()
    else:
        controller.move(angle_to_face,0,0)

    """me.plan = [{'action': Actions.rotateToAngle, 'targetFunction': rotate},
               {'action': Actions.kick, 'targetFunction': kickToAlly}]"""


def receivePass():
    me.goal = Goals.receivePass

    def rotate():
        return me.bearing(ally)

    me.plan = [{'action': Actions.rotateToAngle, 'targetFunction': rotate},
               {'action': Actions.ungrab},
               {'action': Actions.receiveBall},
               {'action': Actions.grab}]


def blockPass():

    def blockHere():
        """move to inbetween two oponents"""
        e0 = enemies[0].currentPoint
        e1 = enemies[1].currentPoint
        x = (e0.x + e1.x)/2
        y = (e0.y + e1.y)/2
        return Point(x, y)

    point_to_be = blockHere()
    angle_to_face = me.bearing(ball)
    angle_to_move = me.bearing(point_to_be)
    distance = me.distance(point_to_be)
    if lineOfSight(e0,e1) == True:
        controller.move(angle_to_face,angle_to_move,distance)
    else:
        if ball.status == enemyA:#move to enemyB
            move_to_b = me.bearing(e1)
            dist_to_b = me.distance(e1)
            controller.move(angle_to_face,move_to_b,dist_to_b)
        else:#move to enemyA
            move_to_a = me.bearing(e0)
            dist_to_a = me.distance(e0)
            controller.move(angle_to_face,move_to_a,dist_to_a)

    """me.plan = [{'action': Actions.moveToPoint, 'targetFunction': blockHere},
               {'action': Actions.rotateToAngle, 'targetFunction': rotate},
               {'action': Actions.ungrab},
               {'action': Actions.receiveBall},
               {'action': Actions.grab}]"""


def guardGoal():#Little faith in this
    """Stop bad people from scoring"""
    angle_to_face = me.bearing(ball)
    distance = me.distance(ourGoal)
    if nearEnough(me.currentPoint[1],ourGoal[1]):

        if ball.status == enemyA:
            ori = enemies[0].orientation
            ori = enemies[0].orientation
            theta = 180 - ori
            x_dist = enemies[1].currentPoint[0]  - ourGoal[0]
            dist = x * tan(ori)
            dis_en = 0
        else:
            ori = enemies[1].orientation
            theta = 180 - ori
            x_dist = enemies[1].currentPoint[0]  - ourGoal[0]
            dist = x * tan(ori)
            dis_en = 1
        if ori >= 180:
            angle_to_move = 90
            distance = me.currentPoint[0] -(enemies[dis_en].currentPoint[0] - dist)
        else:
            angle_to_move = 270
            distance = me.currentPoint[0] +(enemies[dis_en].currentPoint[0] - dist)

        controller.move(angle_to_face,angle_to_move,distance)
    else:
        controller.move(angle_to_face,ourgoal,distance)


    """me.plan = [{'action': Actions.moveToPoint, 'targetFunction': gotoGoal},
               {'action': Actions.rotateToAngle, 'targetFunction': rotate},
               {'action': Actions.moveToPoint,'targetFunction':defend}]"""
