import threading

from constants import *
from globalObjects import me, ally, enemies, robots, ball
from helperClasses import BallStatus, Goals, Actions
from helperFunctions import essentiallyEqual, nearEnough
from actions import moveToPoint, turnToDirection
from goals import collectBall, shoot, passBall, receivePass, blockPass, guardGoal
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
            receivePass()
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
            me.moving = me.currentRotation!=me.rotationHistory[-1]
        except:
            print("oops")
            return

        # if we've already started moving and haven't stopped yet, just keep going.  Why not.
        if me.moving:
            # TODO: add in some kind of checker/corrector
            print("Still going")
            return
        # otherwise:

        # calculate what angle we're aiming for
        targetAngle = me.plan[0]['targetFunction']()

        # if we're at a close enough angle, we're done
        if nearEnough(me.currentRotation, targetAngle):
            print("Done!")
            me.plan.pop(0)
            # start on the next bit of the plan
            executePlan()
            return

        # so if we're not currently turning and we're not yet facing the right directin,
        # send the command to turn to the angle we actually should be at
        else:
            turnToDirection(targetAngle)

    elif currentAction==Actions.moveToPoint:
        #TODO replace with info from 'done' command from robot:
        try:
            me.moving = me.currentPoint!=me.pointHistory[-1]
        except:
            print("oops")
            return

        # if we've already started moving and haven't stopped yet, just keep going.  Why not.
        if me.moving:
            # TODO: add in some kind of checker/corrector
            print("Still going")
            return
        # otherwise:

        # calculate where we're headed
        targetPoint = me.plan[0]['targetFunction']()

        # if we're close enough, we're done
        if nearEnough(me.currentPoint, targetPoint):
            me.plan.pop(0)
            # start on the next bit of the plan
            executePlan()
            return

        # otherwise, ensure we're facing the right direction, and change rotate if not
        if not nearEnough(me.currentRotation, me.bearing(targetPoint)):
            # if we're not facing the right direction, add a step to the plan to face the right way first
            def targetAngle():
                '''Return the angle between us and the point we're headed to in the next step of the plan'''
                # get the index of this action
                i = me.plan.index({'action':Actions.rotateToAngle, 'targetFunction':targetAngle})
                # the target point is the position we're going to in the next action
                targetPoint = me.plan[i+1]['targetFunction']()
                # return the target angle (the bearing from us to the point we're headed to)
                return me.bearing(targetPoint)
            # add the rotation step to the plan
            me.plan.insert(0,{'action':Actions.rotateToAngle,'targetFunction':targetAngle})
            # start carrying out this step this tick
            executePlan()
            return
        # so if we're not currently moving, we're not yet close enough and we're facing the right way,
        # send the command to start moving
        else:
            moveToPoint(targetPoint)

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
        isSim =1
        ourSimulator.tick()
    updatePositions()
    makePlan()
    executePlan()
    threading.Timer(TICK_TIME, tick).start()

# start it off
#tick()
