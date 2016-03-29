from math import sqrt, atan2, degrees
from enum import Enum


class Point(object):
    """A coordinate (x,y) on the pitch

        x (float): the x coordinate
        y (float): the y coordinate

    """
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)


    def distance(self, p):
        """Finds the Euclidean (straight line) distance between two points to 2 decimal places

        Args:
            p (point): the point to find the distance to

        Returns:
            float of the distance between the points in cm

        """
        if not isinstance(p, self.__class__):
            raise TypeError("Point expected, "+p.__class__.__name__+" found")
        return round( sqrt((self.x-p.x)**2+(self.y-p.y)**2) , 2)


    def bearing(self, p):
        """Finds the bearing from this to another point in degrees
        0 is taken to be positive in the x axis
        3 decimal places of accuracy
        if both points are identical, returns 90

        Args:
            p (point): the point to find the bearing to

        Returns:
            float of the bearing between the points, between -180 and 180

        """
        if not isinstance(p, self.__class__):
            raise TypeError("Point expected, "+p.__class__.__name__+" found")
        y = self.y
	x = self.x
        angle = degrees(atan2(self.y - p.y, self.x - p.x))

        bearing1 = (angle + 360) % 360

        bearing2 = (90 - angle) % 360

        print "gb: x=%2d y=%2d angle=%6.1f bearing1=%5.1f bearing2=%5.1f" % ( x, y, angle, bearing1, bearing2)

        xDisplacement = p.x-self.x
        yDisplacement = p.y-self.y
	
        bearing = atan2(yDisplacement,xDisplacement)
	print "Before rounding, the bearing is " + str(degrees(bearing))
        return -round(degrees(bearing), 3)


    def __str__(self):
        return "<"+str(self.x)+","+str(self.y)+">"


    def __repr__(self):
        return str(self)


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.x == other.x and self.y == other.y
        else:
            return False


    def __ne__(self, other):
        return not self.__eq__(other)


class BallStatus(Enum):
    """An enum listing the five different states of the ball, namely not held or held by one of the four robots"""
    free = -1
    me = 0
    ally = 1
    enemyA = 2
    enemyB = 3


class Goals(Enum):
    """An enum listing the possible goals for a robot to have"""
    # if you find yourself with nothing to do, you're probably doing something wrong, but oh well
    none = 0
    collectBall = 1
    passBall = 2
    shoot = 3
    receivePass = 4
    blockPass = 5
    guardGoal = 6
    receiveAndPass = 7

