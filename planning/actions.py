from constants import *
from globalObjects import *
from moveables import Moveable
from helperClasses import Point, BallStatus, Goals
from helperFunctions import sin, cos
from arduinoAPI import turn, move


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

    me.plan = [ {'action':Goals.moveToPoint,'targetFunction':ungrabHere},
                {'action':Goals.ungrab},
                {'action':Goals.moveToPoint,'targetFunction':grabHere},
                {'action':Goals.grab}]


def shoot():
    """Make `shoot` the goal of our robot, and implement the plan for achieving this"""
    # save the plan to the robot
    me.goal = Goals.shoot
    # function to aim at the goal
    def aim():
        return -me.bearing(goalCenter)
    me.plan = [ {'action':Goals.rotateToAngle,'targetFunction': aim},
                {'action':Goals.kick}]


def moveToPoint(point):
    me.moving=True
    if not isinstance(point,Point):
        raise TypeError("Point expected, " + point.__class__.__name__ + " found")
    distance = point.distance(me.currentPoint)
    angle = me.bearing(point) - me.currentRotation
    # ensure the angle is between -180 and 180
    if angle < -180:
        angle+=360
    elif angle > 180:
        angle-=360
    # make that movement
    move(distance, angle)


def turnToDirection(angle):
    me.moving=True
    angleToMove = me.currentRotation-angle
    print("Angle to move:",angleToMove)
    # ensure the angle is between -180 and 80
    if angleToMove < -180:
        angleToMove+=360
    elif angleToMove > 180:
        angleToMove-=360
    #remember, negative is clockwise
    turn(angleToMove)


def interceptObject(target):
    if not isinstance(target,Moveable):
        raise TypeError("Moveable expected, " + point.__class__.__name__ + " found")
    # iteratively work out how long it would take to catch up to the object
    for t in range(0,int(10/TICK_TIME)+1):
        # calculate where you expect it to be at time t
        expectedPosition = target.predictedPosition(t)
        # calculate how far away you expect it to be at time t
        distanceFromMe = me.distance(expectedPosition)
        # calculate how far you could theoretically travel in t seconds
        distanceTravellable = MAX_SPEED*t
        # if you could theoretically travel to that point in t seconds,
        if ( distanceTravellable > distanceFromMe ):
            return expectedPosition
    # if it would take more than 10 seconds to catch up, don't bother trying
    print("Can't catch up")
    return None
