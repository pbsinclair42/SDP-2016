from constants import POINT_ACCURACY, ANGLE_ACCURACY, ITLL_DO_POINT, ITLL_DO_ANGLE
from math import radians, sin as sinr, cos as cosr, tan as tanr
from globalObjects import *
from helperClasses import Point

def essentiallyEqual(a, b):
    """Checks whether two points or two angles are similar enough that
    they're probably the same, give or take vision accuracy

    Args:
        a (point or float): the first point or float (angle) to check if it's
                            similar enough
        b (same as a): the second point or float to check if it's similar enough

    Returns:
        bool  : are the points probably the same?
    """
    try:
        return abs(a.x - b.x) <= POINT_ACCURACY and abs(a.y - b.y) <= POINT_ACCURACY
    except AttributeError:
        return abs(a - b) <= ANGLE_ACCURACY or abs(a + 360 - b) <= ANGLE_ACCURACY or abs(a - 360 - b) <= ANGLE_ACCURACY


def nearEnough(a,b, near_enough_angle=ITLL_DO_ANGLE, near_enough_point=ITLL_DO_POINT):
    """Checks whether two points or two angles are similar enough that we'll work with it

    Args:
        a (point or float): the first point or float to check if it's similar enough
        b (same as a): the second point or float to check if it's similar enough

    Returns:
        bool of whether the two points are similar enough that we'll work with it
    """
    try:
        return abs(a.x-b.x)<=near_enough_point and abs(a.y-b.y)<=near_enough_point
    except AttributeError:
        return abs(a-b)<=near_enough_angle or abs(a+360-b)<=near_enough_angle or abs(a-360-b)<=near_enough_angle


def sin(angle):
    return sinr(radians(angle))

def cos(angle):
    return cosr(radians(angle))

def tan(angle):
    return tanr(radians(angle))

def lineOfSight(From,To):
    dxc = From.x - To.x
    dyc = From.y - To.y

    for obj in globalObjects.moveables:
        dxl = obj.x - To.x
        dyl = obj.y - To.y
        cross = dxc * dyl - dyc * dxl
        if(cross == 0):
            return True
    return False
