import threading

from constants import *
from globalObjects import *
from actions import moveToObject, moveToPoint
import visionAPI

def updatePositions():
    """Updates the system's belief of the state of the game based on the vision system"""

    # get the info on the robots from the vision system
    details = visionAPI.getAllRobotDetails()
    # update the system's beliefs about the robots
    for i in range(0,len(robots)):
        robots[i].update(details[i][0])
        robots[i].rotation=details[i][1]
    # get the info on the ball from the vision system and update the system's beliefs about the ball
    ball.update(visionAPI.getBallCoords())
    ball.status = visionAPI.getBallStatus()


def pickAction():
    """Decide what to do based on the system's current beliefs about the state of play"""
    # TODO
    pass


def tick():
    """Each tick, update your beliefs about the world then decide what action to take based on this"""
    updatePositions()
    pickAction()
    threading.Timer(TICK_TIME, tick).start()

# start it off
#tick()
