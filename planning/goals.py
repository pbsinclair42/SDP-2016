from constants import *
from globalObjects import *
from helperClasses import Point, Goals, Actions
from helperFunctions import sin, cos
from actions import interceptObject


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
