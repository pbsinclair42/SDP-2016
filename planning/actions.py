from constants import *
from globalObjects import *
from moveables import Moveable
from helperClasses import Point
from arduinoAPI import turn, move


def moveToPoint(point):
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
    angleToMove = angle-me.currentRotation
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
