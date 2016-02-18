from constants import *
from globalObjects import *
from helperClasses import Point, Goals, Actions
from helperFunctions import sin, cos
from actions import interceptObject
"""TODO
Position to receive pass - Speak to Other Team About that
Guard goal
Tell teammate plans (?)
"""
def collectBall():
    """Make `collectBall` the goal of our robot, and implement the plan for achieving this"""
    # save the plan to the robot
    me.goal = Goals.collectBall

    # function to calculate where to move to before ungrabbing
    def ungrabHere():
        # work out where we expect to find the ball
        expectedBallPosition = interceptObject(ball)
        # our target is just before that
        bearingAway = expectedBallPosition.bearing(me.currentPoint)
        distanceAway = ROBOT_WIDTH/2 + UNGRAB_DISTANCE
        xDisplacement = round(sin(bearingAway)*distanceAway, 2)
        yDisplacement = round(cos(bearingAway)*distanceAway, 2)
        return Point(expectedBallPosition.x+xDisplacement,expectedBallPosition.y+yDisplacement)
        # Note, if we're already closer than we should be, we'll end up moving back a bit first to avoid knocking it

    # function to calculate where to move to before grabbing
    def grabHere():
        # work out where we expect to find the ball
        expectedBallPosition = interceptObject(ball)
        # our target is just before that
        bearingAway = expectedBallPosition.bearing(me.currentPoint)
        distanceAway = ROBOT_WIDTH/2 + GRAB_DISTANCE
        xDisplacement = round(sin(bearingAway)*distanceAway, 2)
        yDisplacement = round(cos(bearingAway)*distanceAway, 2)
        return Point(expectedBallPosition.x+xDisplacement,expectedBallPosition.y+yDisplacement)

    me.plan = [ {'action':Actions.moveToPoint,'targetFunction':ungrabHere},
                {'action':Actions.ungrab},
                {'action':Actions.moveToPoint,'targetFunction':grabHere},
                {'action':Actions.grab}]


def shoot():
    """Make `shoot` the goal of our robot, and implement the plan for achieving this"""
    # save the plan to the robot
    me.goal = Goals.shoot
    # function to aim at the goal
    def aim():
        return -me.bearing(rightGoalCenter)
    me.plan = [ {'action':Actions.rotateToAngle,'targetFunction': aim},
                {'action':Actions.kick}]


def passBall():

    me.goal = Goals.passBall

    def rotate():
        return me.bearing(ally)

    def kickToAlly():
        return me.distance(ally)
    me.plan = [ {'action':Actions.rotateToAngle,'targetFunction': rotate},
            {'action':Actions.kick,'targetFunction': kickToAlly}]

def recievePass():
    me.goal = Goals.recievePass

    def rotate():
        return me.bearing(ally)
    me.plan = [{'action':Actions.rotateToAngle,'targetFunction':rotate},
               {'action':Actions.ungrab},
               #wait until we have the ball
               {'action':Actions.grab}]

def blockPass():
    me.goal = Goals.blockPass

    def blockHere():
        """move to inbetween two oponents"""
        e0 =enemy0.currentPoint
        e1 = enemy1.currentPoint
        x = sum(e0.x + e1.x)/2
        y = sum(e0.y + e1.y)/2
        return Point(x,y)

    def rotate():
        """rotate to face oponent with ball"""
        me.bearing(ball)
        return me.bearing()
    me.plan = [{'action':Actions.moveToPoint,'targetFunction':blockHere},
               {'action':Actions.rotateToAngle, 'targetFunction':rotate},
               {'action':Actions.ungrab},
                #wait till we have the ball
               {'action':Actions.ungrab}]

def guardGoal()
    """Stop bad people from scoring"""
    me.goal = Goals.guardGoal

    def gotoGoal():
        """Move into position"""
        return leftGoalCenter
    def rotate():
        """rotate into position"""
        return me.bearing(ball)
    def guard():
        """guard until ball moves"""


    me.plan = [{'action':Actions.moveToPoint,'targetFunction':gotoGoal},
               {'action':Actions.rotateToAngle,'targetFunction':rotate}
               """run the guard function"""]
