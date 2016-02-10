import threading

from constants import *
from globalObjects import *
from helperClasses import BallStatus, Goals, essentiallyEqual, nearEnough
from actions import collectBall, shoot
import visionAPI
from arduinoAPI import grab, turn, kick

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
        while action!="1" and action!="2":
            action = raw_input("What action should I do now?\n1. Collect ball\n2. Shoot ball\n? ")
        if action=="1":
            collectBall()
        else:
            shoot()

def executePlan():
    try:
        currentAction = me.plan[0]
    except IndexError:
        print("No actions to execute")
        return
    if currentAction==Goals.rotateToAngle:
        # if it hasn't turned for two ticks
        try:
            oldRotation = me.rotationHistory[-2]
        except IndexError:
            # slightly hacky way of just skipping over this if otherwise
            oldRotation = -200
        if essentiallyEqual(me.currentRotation, oldRotation):
            # check if you're at the right angle
            if nearEnough(me.currentRotation, me.target):
                # if we're close enough already, move on to the next step of the plan
                me.plan.pop(0)
                executePlan()
            # if not, try turning the right amount again
            else:
                turn(me.currentRotation-me.target)
    elif currentAction==Goals.kick:
        # if you've just kicked, you've finished the current goal
        kick(255)
        me.plan.pop(0)
        me.goal = Goals.none


def tick():
    """Each tick, update your beliefs about the world then decide what action to take based on this"""
    updatePositions()
    makePlan()
    executePlan()
    threading.Timer(TICK_TIME, tick).start()

# start it off
#tick()
