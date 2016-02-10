from constants import *
from globalObjects import *
from moveables import Moveable
from helperClasses import Point, BallStatus, Goals
from arduinoAPI import turn

def collectBall():
    #TODO
    pass

def shoot():
    me.goal = Goals.shoot
    me.plan = [Goals.rotateToAngle,Goals.kick]
    print(goalCenter)
    me.target = me.bearing(goalCenter)
    turn(me.currentRotation-me.target)

def moveToObject(target):
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
            # go there
            moveToPoint(expectedPosition)
            return True
    # if it would take more than 10 seconds to catch up, don't bother trying
    print("Can't catch up")
    return False


def moveToPoint(point):
    if not isinstance(point,Point):
        raise TypeError("Point expected, " + point.__class__.__name__ + " found")
    distance = point.distance(me.currentPoint)
    angle = me.bearing(point) - me.currentRotation
    # ensure the angle is between -pi and pi
    if angle < -pi:
        angle+=2*pi
    elif angle > pi:
        angle-=2*pi
    # make that movement
    arduinoAPI.move(distance, angle)
