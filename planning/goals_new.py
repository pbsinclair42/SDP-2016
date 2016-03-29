from constants import *
from globalObjects import *
from helperClasses import Point, Goals, BallStatus
from helperFunctions import sin, cos, tan, nearEnough
import sys
sys.path.append(ROOT_DIR+'comms/')
from RobotController import RobotController
import time
import math
controller = RobotController()
"""TODO
Position to receive pass - Speak to Other Team About that
Guard goal
Tell teammate plans (?)
"""


def collectBall():
    """Make `collectBall` the goal of our robot,
    and implement the plan for achieving this"""
    diff_x = ball.currentPoint.x - me.currentPoint.x
    diff_y = ball.currentPoint.y - me.currentPoint.y
    angle_to_face = math.atan2(-diff_y,diff_x) * (180/3.14)
    #angle_to_face = ball.bearing(Point(0,0))
    angle_to_move = angle_to_face
    distance_to_move = me.distance(ball.currentPoint)
    if ball.status != BallStatus.me:
        print "something - James"
        controller.move(angle_to_face,angle_to_move,distance_to_move,True)
    else:
        print "something - Krassy"

    """me.plan = [{'action': Actions.moveToPoint, 'targetFunction': ungrabHere},
               {'action': Actions.ungrab},
               {'action': Actions.moveToPoint, 'targetFunction': grabHere},
               {'action': Actions.grab}]"""


def shoot():#NEED TO GET THE FUCK OUT OF THERE
    """Make `shoot` the goal of our robot,
    and implement the plan for achieving this"""
    angle_to_face = me.bearing(opponentGoal)#Not 100% convinced on this bearing
    print angle_to_face
    print "^^^^^^^^^^^"
    if nearEnough(me.currentRotation, angle_to_face):
        controller.kick(255)
        print "KICKING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    else:
        print "MOVING TO SHOOT --------------------------------------"

        controller.move(angle_to_face,0,0,False,True)


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
    #TODO
    """
    me.goal = Goals.receivePass

    def rotate():
        return me.bearing(ally)

    me.plan = [{'action': Actions.rotateToAngle, 'targetFunction': rotate},
               {'action': Actions.ungrab},
               {'action': Actions.receiveBall},
               {'action': Actions.grab}]
               """


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


def confuseEnemy():
    """Shoogle around a bit to confuse the enemy and hopefully make them move"""
    # TODO
    # save the plan to the robot
    """
    me.goal = Goals.confuse
    print("NEW GOAL: Confuse the enemy")

    actualDirection = me.currentRotation
    randomRotationAmount = randrange(20,90)

    def firstRotationAmount():
        return actualDirection + randomRotationAmount

    def backAgain():
        return actualDirection

    me.plan = [{'action': Actions.rotateToAngle, 'targetFunction': firstRotationAmount},
               {'action': Actions.rotateToAngle, 'targetFunction': backAgain}]
    """


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

def clearPlan():
    """Reset the robot's goal and plan"""
    # TODO
    """
    me.goal=Goals.none
    print("GOAL CLEAED")
    """