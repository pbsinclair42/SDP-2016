from constants import POINT_ACCURACY, ANGLE_ACCURACY, ITLL_DO_POINT, ITLL_DO_ANGLE
from math import radians, sin as sinr, cos as cosr
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


def nearEnough(a, b):
    #print type(a)
    #print type(b)
    #print a
    #print b
    #a = Point(a[0],a[1])
    #b = Point(b[0],b[1])
    """Checks whether two points or two angles are similar enough
    that we'll work with it

    Args:
        a (point or float): point or float (angle)
        b (same as a)

    Returns:
        bool : are the points close enough?
    """
    try:
        return abs(a.x - b.x) <= ITLL_DO_POINT and abs(a.y - b.y) <= ITLL_DO_POINT
    except AttributeError:
        print "A", a, "B", b
        print "nearEnough:", abs(a - b) <= ITLL_DO_ANGLE, abs(a + 360 - b) <= ITLL_DO_ANGLE, abs(a - 360 - b) <= ITLL_DO_ANGLE
        print "arg1", abs(a - b), "<=", ITLL_DO_ANGLE
        print "arg2", abs(a + 360 - b), "<=", ITLL_DO_ANGLE
        print "arg3", abs(a - 360 - b), "<=", ITLL_DO_ANGLE
        print abs(a - b) <= ITLL_DO_ANGLE or abs(a + 360 - b) <= ITLL_DO_ANGLE or abs(a - 360 - b) <= ITLL_DO_ANGLE
        return abs(a - b) <= ITLL_DO_ANGLE or abs(a + 360 - b) <= ITLL_DO_ANGLE or abs(a - 360 - b) <= ITLL_DO_ANGLE


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


def getHoloVariables(EWBR, EWBY, EWBX):
    theta = EWBR
    h = EWBY
    if ourGoal == rightGoalCenter:
        theta += 180
        if theta > 180:
            theta -= 360
    else:
        h -= PITCH_WIDTH
    # If approaching from the left, then the predicted shot will be EWBX -
    # predict shot, otherwise, EWBX + predictShot.  For encapsulation, I want to
    # calculate the multiplier and then do the predict shot equation elsewhere.
    if ourGoal == rightGoalCenter and EWBX > 0:
        multiplier = -1
    elif ourGoal == leftGoalCenter and EWBX < 0:
        multiplier = -1
    else:
        multiplier = 1

    return theta, h, multiplier


