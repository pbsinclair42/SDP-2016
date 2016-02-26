import threading

from constants import *
from globalObjects import me, ally, enemies, robots, ball 
from helperClasses import BallStatus, Goals, Actions
from helperFunctions import essentiallyEqual, nearEnough
from actions import moveToPoint, turnToDirection
from goals import collectBall, shoot, passBall, recievePass, blockPass, guardGoal
import visionAPI
from arduinoAPI import grab, ungrab, turn, kick, flush, stop, commsSystem as ourSimulator
from simulator import Simulator


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
        while action not in ['1','1b','2','3','4','5','6', '7']:
            print("What action should I do now?")
            action = raw_input("1. Collect ball\n1b. Collect ball using hardware\n2. Shoot ball\n3. Pass ball\n4. Recieve ball\n5. Block pass\n6. Guard Goal\n7. Stop\n? ")
        if action=="1":
            collectBall()
        elif action=="1b":
            collectBall()
            me.plan = [me.plan[2]]
        elif action=="2":
            shoot()
        elif action=="3":
            passBall()
        elif action=="4":
            recievePass()
        elif action=="5":
            blockPass()
        elif action =="6":
            guardGoal()
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

    if currentAction==Actions.rotateToAngle:
        #TODO replace with info from 'done' command from robot:
        try:
            me.moving = me.currentRotation!=me.rotationHistory[-2]
        except:
            print("oops")
        # calculate what angle we're aiming for
        targetAngle = me.plan[0]['targetFunction']()
        # if we've yet to start it turning or we've stopped turning too soon/too late,
        # turn to the angle we actually should be at
        if not me.moving and not nearEnough(me.currentRotation, targetAngle):
            print("turning")
            turnToDirection(targetAngle)
        # if we're close enough, we're done
        elif not me.moving: # and implicitly, nearEnough(me.currentRotation, targetAngle)
            print("Done!")
            me.plan.pop(0)
        # otherwise wait for it to do its stuff
        else:
            print("Still going")

    elif currentAction==Actions.moveToPoint:
        # calculate where we're headed
        targetPoint = me.plan[0]['targetFunction']()
        # if we've yet to start it moving or we've stopped moving too soon/too late,
        # move to the position we actually should be at
        if not me.moving and not nearEnough(me.currentPoint, targetPoint):
            moveToPoint(targetPoint)
        # if we're close enough, we're done
        elif not me.moving: # and implicitly, nearEnough(me.currentPoint, targetPoint)
            me.plan.pop(0)
        # otherwise wait for it to do its stuff
        else:
            # TODO: add in some kind of checker/corrector
            print("Still going")

    elif currentAction==Actions.kick:
        kickDistance = me.plan[0]['targetFunction']()
        kick(kickDistance)
        me.plan.pop(0)
    elif currentAction==Actions.ungrab:
        ungrab()
        me.plan.pop(0)
    elif currentAction==Actions.grab:
        grab()
        me.plan.pop(0)

    # if our plan is over, we've achieved our goal
    if len(me.plan)==0:
        me.goal = Goals.none


def tick():
    """Each tick, update your beliefs about the world then decide what action to take based on this"""
    # if currently simulating, update the simulation
    if isinstance(ourSimulator,Simulator):
        ourSimulator.tick()
    updatePositions()
    makePlan()
    executePlan()
    threading.Timer(TICK_TIME, tick).start()

# start it off
#tick()
