import threading

from constants import *
from globalObjects import me, ally, enemies, robots, ball
from helperClasses import BallStatus, Goals
from actions import executePlan
from goals import collectBall, shoot, passBall, receivePass, blockPass, guardGoal, receiveAndPass
import visionAPI #TODO remove
from world import WorldApi
from CommsAPI import commsSystem


def updatePositions():
    """Updates the system's belief of the state of the game based on the vision system"""
    # get the info on the robots from the vision system

    # old version:
    details = visionAPI.getAllRobotDetails()
    # update the system's beliefs about the robots
    for i in range(0,len(robots)):
        robots[i].update(details[i][0])
        robots[i].updateRotation(details[i][1])
    # get the info on the ball from the vision system and update the system's beliefs about the ball
    currentBallCoords = visionAPI.getBallCoords()
    ball.update(currentBallCoords)

    # new version:
    # visionAPI = WorldApi()

    # update who has the ball - workaround until vision can tell us
    try:
        if ball.distance(enemies[0]) < BALL_OWNERSHIP_DISTANCE:
           ball.status = BallStatus.enemyA
        elif ball.distance(enemies[1]) < BALL_OWNERSHIP_DISTANCE:
           ball.status = BallStatus.enemyB
        elif ball.distance(ally)< BALL_OWNERSHIP_DISTANCE:
           ball.status = BallStatus.ally
        elif ball.distance(me)< BALL_OWNERSHIP_DISTANCE and me.grabbed:
            ball.status = BallStatus.me
        # if we can't see it, assume it's the same, otherwise if it's far enough from everything, it's free
        elif currentBallCoords!=None:
            ball.status = BallStatus.free
    except (TypeError, AttributeError):
        print("Location of some objects unknown")

    # check whether the last command sent has been finished or not
    if commsSystem.am_i_done():
        me.moving=False


def makePlan():
    """Decide what to do based on the system's current beliefs about the state of play"""
    if me.goal == Goals.none:
        if not USING_SIMULATOR:
            commsSystem.restart()
        action = "0"
        while action not in ['1','2','3','4','5','6', '7', '8']:
            print("What action should I do now?")
            action = raw_input("1. Collect ball\n2. Shoot ball\n3. Pass ball\n4. Recieve ball\n5. Block pass\n6. Guard Goal\n7. Receieve and pass (milestoney stuff)\n8. Stop\n? ")
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


def tick():
    """Each tick, update your beliefs about the world then decide what action to take based on this"""
    # if currently simulating, update the simulation
    if USING_SIMULATOR:
        commsSystem.tick()
    updatePositions()
    makePlan()
    executePlan()
    threading.Timer(TICK_TIME, tick).start()

# start it off
if __name__ == "__main__":
    tick()
else:
    updatePositions()
