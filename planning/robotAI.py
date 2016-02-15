import threading

from constants import *
from globalObjects import *
from helperClasses import BallStatus, Goals, essentiallyEqual, nearEnough
from actions import collectBall, shoot, moveToPoint, turnToDirection
import visionAPI
from arduinoAPI import grab, ungrab, turn, kick, flush, stop


def updatePositions():
    """Updates the system's belief of the state of the game based on the vision system"""

    # get the info on the robots from the vision system
    details = visionAPI.getAllRobotDetails()
    # update the system's beliefs about the robots
    for i in range(0,len(robots)):
        robots[i].update(details[i][0])
        robots[i].updateRotation(details[i][1])
    # get the info on the ball from the vision system and update the system's beliefs about the ball
    ball.update(visionAPI.getBallCoords())
    ball.status = visionAPI.getBallStatus()


def makePlan():
    """Decide what to do based on the system's current beliefs about the state of play"""
    if me.goal == Goals.none:
        action = "0"
        while action not in ['1','1b','2','3']:
            print("What action should I do now?")
            action = raw_input("1. Collect ball\n1b. Collect ball using hardware\n2. Shoot ball\n3. Stop\n? ")
        if action=="1":
            collectBall()
        elif action=="1b":
            collectBall()
            me.plan = [me.plan[2]]
        elif action=="2":
            shoot()
        else:
            import sys
            sys.exit()


def executePlan():
    """Check whether the action you're currently performing has finished and move to the next action if so"""
    try:
        currentAction = me.plan[0]['action']
    except IndexError:
        print("No actions to execute")
        return

    if currentAction==Goals.rotateToAngle:
        # calculate what angle we're aiming for
        targetAngle = me.plan[0]['targetFunction']()/2
        # if we've yet to start it turning, start it now
        if not me.moving and not nearEnough(me.currentRotation, targetAngle):
            print("turning")
            turnToDirection(targetAngle)
        # if we're close enough, we're done
        elif not me.moving: # and implicitly, nearEnough(me.currentRotation, targetAngle)
            print("Done!")
            me.plan.pop(0)
        # if not, stop if we've arrived
        elif nearEnough(me.currentRotation, targetAngle):
            print("Stopped!")
            stop()

        # otherwise check if it's stopped, and restart it if so, otherwise wait for it to do its stuff
        else:
            # check if it's not turned for the past two ticks
            try:
                oldRotation = me.rotationHistory[-2]
            except IndexError:
                print("Not enough history yet")
                # slightly hacky way of just skipping over this if otherwise
                oldRotation = -200
            # if it hasn't turned for two ticks
            if essentiallyEqual(me.currentRotation, oldRotation):
                print("It's stopped itself!")
                # we're assuming that we've stopped turning, but stop to make sure
                stop()
                # check if you're at the right angle
                if nearEnough(me.currentRotation, targetAngle):
                    # if we're close enough already, move on to the next step of the plan
                    me.plan.pop(0)
            else:
                print("Still going")

    elif currentAction==Goals.moveToPoint:
        # calculate where we're headed
        targetPoint = me.plan[0]['targetFunction']()
        # if we've yet to start it moving, start it now
        if not me.moving and not nearEnough(me.currentPoint, targetPoint):
            moveToPoint(targetPoint)
        # if we're close enough, we're done
        elif not me.moving: # and implicitly, nearEnough(me.currentPoint, targetPoint)
            me.plan.pop(0)
        # if not, stop if we've arrived
        elif nearEnough(me.currentPoint, targetPoint):
            stop()
        #TODO: go back if you overshoot
        # otherwise check if it's stopped, and restart it if so, otherwise wait for it to do its stuff
        else:
            # check if it's not moved for the past two ticks
            try:
                oldPoint = me.pointHistory[-2]
            except IndexError:
                print("Not enough history yet")
                # slightly hacky way of just skipping over this if otherwise
                oldPoint = Point(-2000,-2000)
            # if it hasn't moved for two ticks
            if essentiallyEqual(me.currentPoint, oldPoint):
                # we're assuming that we've stopped moving, but stop to make sure
                stop()
                # check if you're at the right position
                if nearEnough(me.currentPoint, targetPoint):
                    # if we're close enough already, move on to the next step of the plan
                    me.plan.pop(0)

    elif currentAction==Goals.kick:
        # TODO: add power function for kicking
        kick(200)
        # TODO include me.plan.pop(0)
    elif currentAction==Goals.ungrab:
        ungrab()
        me.plan.pop(0)
    elif currentAction==Goals.grab:
        grab()
        me.plan.pop(0)

    # if our plan is over, we've achievd our goal
    if len(me.plan)==0:
        me.goal = Goals.none



def tick():
    """Each tick, update your beliefs about the world then decide what action to take based on this"""
    updatePositions()
    makePlan()
    executePlan()
    threading.Timer(TICK_TIME, tick).start()

# start it off
#tick()
