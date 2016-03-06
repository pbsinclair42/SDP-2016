import threading
import math

from constants import *
from globalObjects import me, ally, enemies, robots, ball
from helperClasses import BallStatus, Goals, Actions
from helperFunctions import essentiallyEqual, nearEnough
from actions import moveToPoint, turnToDirection
from goals import collectBall, shoot, passBall, receivePass, blockPass, guardGoal, receiveAndPass
import visionAPI
from CommsAPI import grab, ungrab, turn, kick, flush, stop, commsSystem
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
    currentBallCoords = visionAPI.getBallCoords()
    ball.update(currentBallCoords)
    ball.status = visionAPI.getBallStatus()

    #update who has the ball - workaround until vision can tell us
    try:
        if ball.distance(enemies[0]) < BALL_OWNERSHIP_DISTANCE:
           ball.status = BallStatus.enemyA
        elif ball.distance(enemies[1]) < BALL_OWNERSHIP_DISTANCE:
           ball.status = BallStatus.enemyB
        elif ball.distance(ally)< BALL_OWNERSHIP_DISTANCE:
           ball.status = BallStatus.ally
        elif ball.distance(me)< BALL_OWNERSHIP_DISTANCE and me.grabberState == 0:
            ball.status = BallStatus.me
        # if we can't see it, assume it's the same, otherwise if it's far enough from everything, it's free
        elif currentBallCoords!=None:
            ball.status = BallStatus.free
    except (TypeError, AttributeError):
        print("Location of some objects unknown")
    print(ball.status)
    # check if the last command we sent to the robot has finished
    #newCommandFinished = me.lastCommandFinished != commsSystem.current_cmd()
    #if newCommandFinished:
    if commsSystem.am_i_done():
        me.lastCommandFinished+=1
        me.moving=False
    else:
        print"Not done"


def makePlan():
    """Decide what to do based on the system's current beliefs about the state of play"""
    if me.goal == Goals.none:
        if not USING_SIMULATOR:
            commsSystem.restart()
        action = "0"
        while action not in ['1','2','3','4','5','6', '7', '8']:
            print("What action should I do now?")
            action = raw_input("1. Collect ball\n1b. Collect ball using hardware\n2. Shoot ball\n3. Pass ball\n4. Recieve ball\n5. Block pass\n6. Guard Goal\n7. Receieve and pass (milestoney stuff)\n8. Stop\n? ")
        if action=="1":
            collectBall()
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
        elif action == "7":
            receiveAndPass()
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
        # if we've already started moving and haven't stopped yet, just keep going.  Why not.
        if me.moving:
            # TODO: add in some kind of checker/corrector
            print("Still doing stuff")
        else:
            # calculate what angle we're aiming for
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

    elif currentAction==Actions.moveToPoint:
        # if we've already started moving and haven't stopped yet, just keep going.  Why not.
        if me.moving:
            # TODO: add in some kind of checker/corrector
            print("Still doing stuff")
        else:
            # calculate where we're headed
            targetPoint = me.plan[0]['targetFunction']()

            # if we're close enough, we're done
            if nearEnough(me.currentPoint, targetPoint):
                me.plan.pop(0)
                # start on the next bit of the plan
                executePlan()

            elif not nearEnough(me.currentRotation, me.bearing(targetPoint)):
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

            # so if we're not currently moving, we're not yet close enough and we're facing the right way,
            # send the command to start moving
            else:
                moveToPoint(targetPoint)

    elif currentAction==Actions.kick:
        if me.moving:
            print("Still doing stuff")
        else:
            kickDistance = me.plan[0]['targetFunction']()
            kick(kickDistance)
            me.plan.pop(0)

    elif currentAction==Actions.ungrab:
        if me.moving:
            print("Still doing stuff")
        else:
            ungrab()
            me.grabberState=1
            me.plan.pop(0)

    elif currentAction==Actions.grab:
        if me.moving:
            print("Still doing stuff")
        else:
            grab()
            me.grabberState=0
            me.plan.pop(0)

    elif currentAction == Actions.receiveBall:
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
                    grab()
                    collectBall()

    # if our plan is over, we've finished our goal
    if len(me.plan)==0:
        me.goal = Goals.none


def tick():
    """Each tick, update your beliefs about the world then decide what action to take based on this"""
    # if currently simulating, update the simulation
    if USING_SIMULATOR:
        commsSystem.tick()
    updatePositions()
    #print(me.lastCommandFinished, commsSystem.current_cmd())
    makePlan()
    executePlan()
    threading.Timer(TICK_TIME, tick).start()

# start it off
#tick()
'''
updatePositions()
updatePositions()
from helperClasses import Point
me.plan=[{'action':Actions.moveToPoint,'targetFunction':lambda:Point(80,80)}]
me.goal = Goals.collectBall'''
updatePositions()
tick()
