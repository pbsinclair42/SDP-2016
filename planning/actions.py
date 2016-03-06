from constants import *
from globalObjects import *
from moveables import Moveable, Ball
from helperClasses import Point
from CommsAPI import turn, move

def kick():
    if me.moving:
        print("Still doing stuff")
    else:
        kickDistance = me.plan[0]['targetFunction']()
        kick(kickDistance)
        me.plan.pop(0)

def ungrab():
    if me.moving:
        print("Still doing stuff")
    else:
        ungrab()
        me.grabberState=1
        me.plan.pop(0)

def grab():
    if me.moving:
        print("Still doing stuff")
    else:
        grab()
        me.grabberState=0
        me.plan.pop(0)

def guardGoal():
    if ball.moving == False:
        turnToDirection(me.bearing(ball))
    elif ball.moving and (me.distance(ball.predictedPosition(10)) < me.distance(ball)):# ballcoming towardsa us:
        executePlan()
    elif ball.moving:# ball moving but not towards us
        me.interceptObject(ball)
        me.plan.pop(0)

def recieveBall():
    if me.moving:
        print("Still doing stuff")
    else:
        # if another robot's still holding the ball, just wait
            # TODO: maybe reposition if need be?
        if ball.status!=BallStatus.free:
                print("Ball's not been kicked yet lol")
            # if the ball's been kicked, we hope to collect it
        else:
            # if it's headed towards us, stay where we are
            if nearEnough(ball.direction, ball.bearing(me)):
                    # if it's close enough, we're done
                if ball.distance(me)<ROBOT_WIDTH + GRAB_DISTANCE:
                    me.plan.pop(0)
                    # otherwise, just staying here is cool
                # if it's not headed towards us, just try and fetch it
            else:
                # go to where its actually going
                collectBall()

def rotateToAngle():
    if me.moving:
        # TODO: add in some kind of checker/corrector
        print("Still doing stuff")
    else:
        #calculate the angle we're aming for
        targetAngle = me.plan[0]['targetFunction']()
         # if we're at a close enough angle, we're done
        if nearEnough(me.currentRotation, targetAngle):
            print("Done!")
            me.plan.pop(0)
            # start on the next bit of the plan
            executePlan()

        # so if we're not currently turning and we're not yet facing the right directin,
        # send the command to turn to the angle we actually should be at
    else:
        turnToDirection(targetAngle)


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
    # ensure the angle is between -180 and 80
    if angleToMove < -180:
        angleToMove+=360
    elif angleToMove > 180:
        angleToMove-=360
    #remember, negative is clockwise
    turn(angleToMove)


def interceptObject(target):
    #return target.currentPoint
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


