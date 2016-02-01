from math import sin, cos

from constants import *
from helperClasses import Point, BallStatus


class Moveable(object):
    """An object in the game that can move (ie robot or ball)"""
    #TODO: walls
    _HISTORY_SIZE = 4

    def __init__(self, p=None):
        if p==None:
            self.currentPoint=None
            self.pointHistory=[]
            # speed is in units per tick
            self.currentSpeed=None
            self.speedHistory=[]
            # note that direction corresponds to direction of movement and not necessarily the direction the object is facing
            self.direction=None
            # acceleration is in units per tick per tick
            self.acceleration=None
        else:
            if not isinstance(p,Point):
                raise TypeError("Point expected, " + p.__class__.__name__ + " found")
            self.currentPoint=p
            self.pointHistory=[p]
            self.currentSpeed=None
            self.speedHistory=[]
            self.direction=None
            self.acceleration=None


    def update(self, newPoint):
        """Update the object with the position it's in this new tick.  To be called every tick.  

        Args:
            newPoint (Point): the new coordinates of this object

        """
        # save the new position
        self.currentPoint = newPoint
        self.pointHistory.append(newPoint)
        # only store a max of _HISTORY_SIZE points in the history
        if len(self.pointHistory)>self._HISTORY_SIZE:
            self.pointHistory.pop(0)

        # calculate and save the current direction
        self.direction = self.pointHistory[0].bearing(self.pointHistory[-1])

        # calculate and save the new speed
        try:
            newSpeed=self.pointHistory[0].distance(self.pointHistory[-1])/(len(self.pointHistory)-1)
            self.speedHistory.append(newSpeed)
            self.currentSpeed = newSpeed
            # only store a max of _HISTORY_SIZE-1 points in the history
            if len(self.speedHistory) > self._HISTORY_SIZE-1:
                self.speedHistory.pop(0)
        except ZeroDivisionError:
            pass

        # calculate and save the new acceleration
        try:
            self.acceleration = (self.speedHistory[-1]-self.speedHistory[0])/(len(self.speedHistory)-1)
        except (ZeroDivisionError, IndexError):
            # if we don't have enough data to calculate an acceleration (not enough speeds recorded), wait for now
            pass


    def predictedPosition(self, t):
        """Calculate the position of the object in t seconds if it continues accelerating at its current rate

        Args:
            t (float): the number of seconds into the future you're predicting the object's position.
                       Note that the large t gets, the less accurate the prediction will be.

        Returns:
            Point of the predicted position of the object

        """
        displacement = self.currentSpeed*t + 0.5*self.acceleration*(t**2)
        xDisplacement = round(sin(self.direction)*displacement, 2)
        yDisplacement = round(cos(self.direction)*displacement, 2)
        return Point(self.currentPoint.x+xDisplacement, self.currentPoint.y+yDisplacement)


    def distance(self, other):
        """Finds the Euclidean (straight line) distance between this object and another

        Args:
            other (Moveable or Point): the moveable or point to find the distance to

        Returns:
            float of the distance between the two in units

        """
        if isinstance(other,Moveable):
            return self.currentPoint.distance(other.currentPoint)
        elif isinstance(other,Point):
            return self.currentPoint.distance(other)
        else:
            raise TypeError("Moveable or Point expected, " + point.__class__.__name__ + " found")


    def bearing(self, other):
        """Finds the bearing from this object to another in radians

        Args:
            other (Moveable or Point): the moveable or point to find the bearing to

        Returns:
            float of the bearing between the two, between -pi and pi

        """
        if isinstance(other,Moveable):
            return self.currentPoint.bearing(other.currentPoint)
        elif isinstance(other,Point):
            return self.currentPoint.bearing(other)
        else:
            raise TypeError("Moveable or Point expected, " + point.__class__.__name__ + " found")


    def __str__(self):
        return str(self.__class__.__name__)+str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class Robot(Moveable):
    def __init__(self, p=None):
        super(Robot,self).__init__(p)
        self.currentRotation=0


class Ball(Moveable):
    def __init__(self, p=None):
        super(Ball,self).__init__(p)
        self.status=BallStatus.free

'''
#for testing
#TODO: remove
a=Moveable(Point(0,0))
a.update(Point(1,0))
a.update(Point(3,0))
'''
