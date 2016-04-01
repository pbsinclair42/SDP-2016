from constants import POINT_ACCURACY, ANGLE_ACCURACY, ITLL_DO_POINT, ITLL_DO_ANGLE
from math import radians, sin as sinr, cos as cosr, tan as tanr
from helperClasses import Point
import globalObjects

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

def isEnemyBox(Point):#checks if the point is in the enemys defence box
    if globalObjects.ourGoal == globalObjects.leftGoalCenter:
        if Point.x >= globalObjects.PITCH_LENGTH - 90 and Point.y >= 50 and Point.y <= globalObjects.PITCH_WIDTH-50:
            print "Can't Go There"
            return True
        else:
            return False
    if globalObjects.ourGoal == globalObjects.rightGoalCenter:
        if Point.x <= 90 and Point.y >= 50 and Point.y <= globalObjects.PITCH_WIDTH-50:
            print "Can't Go There"
            return True
        else:
            return False

def isOurBoxFree(Point):#checks if the point is in the enemys defence box
    if globalObjects.ourGoal == globalObjects.rightGoalCenter:
        if Point.x >= globalObjects.PITCH_LENGTH - 90 and Point.y >= 50 and Point.y <= globalObjects.PITCH_WIDTH-50:
            print "Can't Go There"
            return True
        else:
            return False
    if globalObjects.ourGoal == globalObjects.leftGoalCenter:
        if Point.x <= 90 and Point.y >= 50 and Point.y <= globalObjects.PITCH_WIDTH-50:
            print "Can't Go There"
            return True
        else:
            return False

def lineOfSight(From,To):
    dxc = From.x - To.x
    dyc = From.y - To.y

    for obj in globalObjects.moveables:
        
        try:
            ox = obj.x
        except:
            ox = obj.currentPoint.x
        try:
            oy = obj.y
        except:
            oy = obj.currentPoint.y
        
        x1 = From.x
        x2 = To.x
        y1 = From.y
        y2 = To.y
        x3 = ox
        y3 = oy
        
        distance = abs((y2 - y1) * x3 - (x2 - x1) * y3 + x2 * y1 - x1 * y2)
        distance = distance /(( ((y2 - y1)**2) + ((x2 - x1) **2)) ** 0.5)
        
        if distance != 0.0 and distance < 20:
            return False
    return True