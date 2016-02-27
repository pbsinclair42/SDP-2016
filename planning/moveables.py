from constants import *
from helperClasses import Point, BallStatus, Goals
from helperFunctions import sin, cos


class Moveable(object):
    """An object in the game that can move (ie robot or ball)"""
    #TODO: walls
    _HISTORY_SIZE = 10

    def __init__(self, p=None):
        if p==None:
            self.currentPoint=None
            self.pointHistory=[]
            # speed is in xm per tick
            self.currentSpeed=None
            self.speedHistory=[]
            # note that direction corresponds to direction of movement and not necessarily the direction the object is facing
            self.direction=None
            # acceleration is in cm per tick per tick
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
        # if we've temporarily lost the object, assume it's in the same place
        if newPoint==None:
            newPoint=self.currentPoint
            print("Lost position of "+(self.name if self.name!=None else "moveable"))
        # if we've yet to find the robot, don't bother updating anything
        if newPoint!=None:
            # save the old point
            if self.currentPoint!=None:
                self.pointHistory.append(self.currentPoint)
            # save the new position
            self.currentPoint = newPoint
            # only store a max of _HISTORY_SIZE points in the history
            if len(self.pointHistory)>self._HISTORY_SIZE:
                self.pointHistory.pop(0)

            try:
                # calculate and save the current direction
                self.direction = self.pointHistory[0].bearing(self.pointHistory[-1])
            except IndexError:
                # if we don't have enough information to calculate a direction, wait for now
                pass

            # calculate and save the new speed
            try:
                newSpeed=self.pointHistory[0].distance(self.pointHistory[-1])/(len(self.pointHistory)-1)
                newSpeed = round(newSpeed, 2)
                self.speedHistory.append(newSpeed)
                self.currentSpeed = newSpeed
                # only store a max of _HISTORY_SIZE-1 points in the history
                if len(self.speedHistory) > self._HISTORY_SIZE-1:
                    self.speedHistory.pop(0)
            except (ZeroDivisionError, IndexError):
                pass

            # calculate and save the new acceleration
            try:
                acceleration = (self.speedHistory[-1]-self.speedHistory[0])/(len(self.speedHistory)-1)
                self.acceleration = round(acceleration, 3)
            except (ZeroDivisionError, IndexError):
                # if we don't have enough data to calculate an acceleration (not enough speeds recorded), wait for now
                pass


    def predictedPosition(self, t):
        """Calculate the position of the object in t ticks if it continues accelerating at its current rate

        Args:
            t (int): the number of ticks into the future you're predicting the object's position.
                       Note that the large t gets, the less accurate the prediction will be.

        Returns:
            Point of the predicted position of the object

        """
        try:
            displacement = self.currentSpeed*t + 0.5*self.acceleration*(t**2)
            xDisplacement = round(sin(self.direction)*displacement, 2)
            yDisplacement = round(cos(self.direction)*displacement, 2)
            return Point(self.currentPoint.x+xDisplacement, self.currentPoint.y+yDisplacement)
        except TypeError:
            if isinstance(t,int):
                return self.currentPoint
            else:
                raise TypeError("Float expected, " + t.__class__.__name__ + " found")


    def distance(self, other):
        """Finds the Euclidean (straight line) distance between this object and another

        Args:
            other (Moveable or Point): the moveable or point to find the distance to

        Returns:
            float of the distance between the two in cm

        """
        if isinstance(other,Moveable):
            return self.currentPoint.distance(other.currentPoint)
        elif isinstance(other,Point):
            return self.currentPoint.distance(other)
        else:
            raise TypeError("Moveable or Point expected, " + other.__class__.__name__ + " found")


    def bearing(self, other):
        """Finds the bearing from this object to another in degrees

        Args:
            other (Moveable or Point): the moveable or point to find the bearing to

        Returns:
            float of the bearing between the two, between -180 and 180

        """
        if isinstance(other,Moveable):
            return self.currentPoint.bearing(other.currentPoint)
        elif isinstance(other,Point):
            return self.currentPoint.bearing(other)
        else:
            raise TypeError("Moveable or Point expected, " + other.__class__.__name__ + " found")


    def __str__(self):
        return str(self.__class__.__name__)+str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class Robot(Moveable):
    def __init__(self, p=None, name=None):
        super(Robot,self).__init__(p)
        # the direction the robot is facing, as detected by the vision system
        self.currentRotation=None
        self.rotationHistory=[]
        # purely used for warning/error messages
        self.name=name
        # the high level goal of the robot
        self.goal = Goals.none
        # the plan of the robot
        self.plan=[]
        # if we've told the robot to move or rotate and haven't noticed it stop doing so
        self.moving = False

    def updateRotation(self, rotation):
        """Update the rotation with a new value

        If the vision system failed to find the rotation of the robot this frame,
        just assume the rotation hasn't changed

        Args:
            rotation (float): the direction the robot is facing in degrees"""
        if self.currentRotation!=None:
            # only store a max of _HISTORY_SIZE points in the history
            if len(self.rotationHistory)>self._HISTORY_SIZE:
                self.rotationHistory.pop(0)
            self.rotationHistory.append(self.currentRotation)
        if rotation!=None:
            self.currentRotation= rotation


class Ball(Moveable):
    def __init__(self, p=None, name=None):
        super(Ball,self).__init__(p)
        self.status=BallStatus.free
        self.name=name
