from constants import *
from globalObjects import *
from helperClasses import Point, Goals, Actions
from helperFunctions import sin, cos
from actions import *
import time
from random import randrange

"""TODO
Position to receive pass - Speak to Other Team About that
Guard goal
Tell teammate plans (?)
"""


def collectBall():
    """Make `collectBall` the goal of our robot,
    and implement the plan for achieving this"""
    # save the plan to the robot
    me.goal = Goals.collectBall
    print("NEW GOAL: Collect ball")

    # function to calculate where to move to before ungrabbing
    def ungrabHere():
        # work out where we expect to find the ball
        # TODO: replace with interceptObject(ball)?
        expectedBallPosition = ball.currentPoint
        # our target is just before that
        bearingAway = expectedBallPosition.bearing(me.currentPoint)
        distanceAway = ROBOT_WIDTH + UNGRAB_DISTANCE
        xDisplacement = round(cos(bearingAway)*distanceAway, 2)
        yDisplacement = -round(sin(bearingAway)*distanceAway, 2)
        unGrabX = expectedBallPosition.x+xDisplacement
        unGrabY = expectedBallPosition.y+yDisplacement
        return Point(unGrabX, unGrabY)
        # Note, if we're already closer than we should be,
        # we'll end up moving back a bit first to avoid knocking it

    # function to calculate where to move to before grabbing
    def grabHere():
        # work out where we expect to find the ball
        # TODO: replace with interceptObject(ball)?
        expectedBallPosition = ball.currentPoint
        # our target is just before that
        bearingAway = expectedBallPosition.bearing(me.currentPoint)
        distanceAway = ROBOT_WIDTH + GRAB_DISTANCE
        xDisplacement = round(cos(bearingAway)*distanceAway, 2)
        yDisplacement = -round(sin(bearingAway)*distanceAway, 2)
        grabX = expectedBallPosition.x+xDisplacement
        grabY = expectedBallPosition.y+yDisplacement
        return Point(grabX, grabY)

    me.plan = [{'action': Actions.moveToPoint, 'targetFunction': ungrabHere},
               {'action': Actions.ungrab},
               {'action': Actions.moveToPoint, 'targetFunction': grabHere},
               {'action': Actions.grab}]


def shoot():
    """Make `shoot` the goal of our robot,
    and implement the plan for achieving this"""
    # save the plan to the robot
    me.goal = Goals.shoot
    print("NEW GOAL: Shoot")

    # work out how far to kick the ball
    def distanceToKick():
        return 255  # maybe change to be more accurate? can shoot with max power

    def aim():
        return me.bearing(opponentGoal)

    me.plan = [{'action': Actions.rotateToAngle, 'targetFunction': aim},
               {'action': Actions.kick, 'targetFunction': distanceToKick}]


def confuseEnemy():
    """Shoogle around a bit to confuse the enemy and hopefully make them move"""
    # save the plan to the robot
    me.goal = Goals.confuse
    print("NEW GOAL: Confuse the enemy")

    actualDirection = me.currentRotation
    randomRotationAmount = randrange(20,90)

    def firstRotationAmount():
        return actualDirection + randomRotationAmount

    def backAgain():
        return actualDirection

    me.plan = [{'action': Actions.rotateToAngle, 'targetFunction': firstRotationAmount},
               {'action': Actions.rotateToAngle, 'targetFunction': backAgain}]


def receiveAndPass():
    me.goal = Goals.receiveAndPass

    """Stop bad people from scoring and pass ball to ally"""
    def rotate1():
        """rotate into position"""
        return me.bearing(ball)

    def rotate2():
        return me.bearing(ally)

    def kickToAlly():
        return 255  # me.distance(ally)

    me.plan = [{'action': Actions.rotateToAngle, 'targetFunction': rotate1},
               {'action': Actions.ungrab},
               {'action': Actions.receiveBallForPass},
               {'action': Actions.grab},
               {'action': Actions.rotateToAngle, 'targetFunction': rotate2},
               {'action': Actions.kick, 'targetFunction': kickToAlly}]


def passBall():
    me.goal = Goals.passBall
    print("NEW GOAL: Pass")

    def rotate():
        return me.bearing(ally)

    def kickToAlly():
        return 255  # me.distance(ally)

    me.plan = [{'action': Actions.rotateToAngle, 'targetFunction': rotate},
               {'action': Actions.kick, 'targetFunction': kickToAlly}]


def receivePass():
    me.goal = Goals.receivePass
    print("NEW GOAL: Receive pass")

    def rotate():
        return me.bearing(ally)

    me.plan = [{'action': Actions.rotateToAngle, 'targetFunction': rotate},
               {'action': Actions.ungrab},
               {'action': Actions.receiveBall},
               {'action': Actions.grab}]


def blockPass():
    me.goal = Goals.blockPass
    print("NEW GOAL: Intercept enemy pass")

    def blockHere():
        """move to inbetween two oponents"""
        e0 = enemies[0].currentPoint
        e1 = enemies[1].currentPoint
        x = (e0.x + e1.x)/2
        y = (e0.y + e1.y)/2
        return Point(x, y)

    def rotate():
        """rotate to face oponent with ball"""
        return me.bearing(ball)

    me.plan = [{'action': Actions.moveToPoint, 'targetFunction': blockHere},
               {'action': Actions.rotateToAngle, 'targetFunction': rotate},
               {'action': Actions.ungrab},
               {'action': Actions.receiveBall},
               {'action': Actions.grab}]


def guardGoal():
    """Stop bad people from scoring"""
    me.goal = Goals.guardGoal
    print("NEW GOAL: Guard our goal")

    def gotoGoal():
        """Move into position"""
        # move to the top of the goal
        return ourGoal

    def rotate():
        """rotate into position"""
        return me.bearing(opponentGoal)

    def defend():
        """Get the Y coord of ball to try and defend the goal"""
        ballY = ball.currentPoint.y
        minY = PITCH_WIDTH/2 - 0.5*GOAL_WIDTH + ROBOT_WIDTH/2
        maxY = PITCH_WIDTH/2 + 0.5*GOAL_WIDTH - ROBOT_WIDTH/2
        ballY = max(minY, min(maxY, ballY))
        return Point(ourGoal.x,ballY)

    me.plan = [{'action': Actions.moveToPoint, 'targetFunction': gotoGoal},
               {'action': Actions.rotateToAngle, 'targetFunction': rotate},
               {'action': Actions.defend,'targetFunction':defend}]

def clearPlan():
    """Reset the robot's goal and plan"""
    me.goal=Goals.none
    me.plan=[]
    print("GOAL CLEAED")