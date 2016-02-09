import threading

from constants import *
from globalObjects import *
from helperClasses import BallStatus
from actions import moveToObject, moveToPoint
import visionAPI
from arduinoAPI import grab

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


def pickAction():
    """Decide what to do based on the system's current beliefs about the state of play"""
    # TODO: replace this with sensible plans
    if ball.status == BallStatus.free or ball.status == BallStatus.me:
        if me.distance(ball)<ally.distance(ball):
            if me.distance(ball)<GRAB_DISTANCE:
                grab()
            else:
                moveToObject(ball)


def tick():
    """Each tick, update your beliefs about the world then decide what action to take based on this"""
    updatePositions()
    pickAction()
    threading.Timer(TICK_TIME, tick).start()

# start it off
#tick()
