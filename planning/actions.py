from constants import *
from globalObjects import *
from moveables import Moveable
from helperClasses import Point, BallStatus
from arduinoAPI import *


def moveToObject(target):
    if not isinstance(target,Moveable):
        raise TypeError("Moveable expected, " + point.__class__.__name__ + " found")
    # TODO


def moveToPoint(point):
    if not isinstance(point,Point):
        raise TypeError("Point expected, " + point.__class__.__name__ + " found")
    distance = point.distance(me.currentPoint)
    angle = me.currentPoint.bearing(point) - me.currentRotation
    # ensure the angle is between -pi and pi
    if angle < -pi:
        angle+=2*pi
    elif angle > pi:
        angle-=2*pi
    move(distance, angle)
