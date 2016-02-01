from math import sqrt, atan, pi
from enum import Enum

class Point(object):
    """A coordinate (x,y) on the pitch

    Attributes:
        x (float): the x coordinate
        y (float): the y coordinate

    """
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)


    def distance(self, p):
        """Finds the Euclidean (straight line) distance between two points

        Args:
            p (point): the point to find the distance to

        Returns:
            float of the distance between the points in units

        """
        if not isinstance(p, self.__class__):
            raise TypeError("Point expected, "+p.__class__.__name__+" found")
        return sqrt((self.x-p.x)**2+(self.y-p.y)**2)


    def bearing(self, p):
        """Finds the bearing between two points in radians, where 0 is positive in the y axis

        Args:
            p (point): the point to find the bearing to

        Returns:
            float of the bearing between the points

        """
        if not isinstance(p, self.__class__):
            raise TypeError("Point expected, "+p.__class__.__name__+" found")
        xDisplacement = p.x-self.x
        yDisplacement = p.y-self.y
        # ensure no division by zero occurs
        if yDisplacement==0:
            return pi/2 if xDisplacement>=0 else 3*pi/2
        interiorAngle = atan(abs(xDisplacement)/abs(yDisplacement))
        if xDisplacement>=0 and yDisplacement>=0:
            return interiorAngle
        elif xDisplacement>=0: # and implicitly, yDisplacement<0
            return pi - interiorAngle
        elif yDisplacement<0: # and implicitly, xDisplacement<0
            return pi + interiorAngle
        else: # implicitly xDisplacement<0 and yDisplacement>=0
            return 2*pi - interiorAngle
   

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

