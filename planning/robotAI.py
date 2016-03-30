import threading

from constants import *
from globalObjects import me, ally, enemies, ball
from helperClasses import BallStatus, Goals, Point
from goals_new import collectBall, shoot, passBall, receivePass, blockPass, guardGoal, confuseEnemy
from helperFunctions import nearEnough, lineOfSight
from strategy import Actually_play_ball, playBall
from world import WorldApi
import math

def updatePositions():
    """Updates the system's belief of the state of the game based on the vision system"""
    # get the info on the robots from the vision system
    if api.getMyPosition() is not None:
        mePosition = api.getMyPosition()
        me.update(Point(mePosition[0]*X_RATIO,mePosition[1]*Y_RATIO))
    else:
        print "Can't find my position this tick :("
    if api.getMyOrientation()[1] is not None:
        meOrientation = api.getMyOrientation()[1]
        me.updateRotation(meOrientation)
    else:
        print "Can't find my orientation this tick :("

    if api.getAllyPosition() is not None:
        allyPosition = api.getAllyPosition()
        ally.update(Point(allyPosition[0]*X_RATIO,allyPosition[1]*Y_RATIO))
    else:
        print "Can't find my friend's position this tick :("
    try:
        if api.getAllyOrientation()[1] is not None:
            allyOrientation = api.getAllyOrientation()[1]
            ally.updateRotation(allyOrientation)
    except:
        print "lol no"
    else:
        print "Can't find my friend's orientation this tick :("

    if api.getEnemyPositions()[0] is not None:
        enemy0Position = api.getEnemyPositions()[0]
        enemies[0].update(Point(enemy0Position[0]*X_RATIO,enemy0Position[1]*Y_RATIO))
    else:
        print "Can't find enemy 0 this tick :("
    if api.getEnemyOrientation()[0] is not None:
        enemy0Orientation =  api.getEnemyOrientation()[0][1]
        enemies[0].updateRotation(enemy0Orientation)
    else:
        print "Can't find enemy 0's orientation this tick :("

    if api.getEnemyPositions()[1] is not None:
        enemy1Position = api.getEnemyPositions()[1]
        enemies[1].update(Point(enemy1Position[0]*X_RATIO,enemy1Position[1]*Y_RATIO))
    else:
        print "Can't find enemy 1 this tick :("
    if api.getEnemyOrientation()[1] is not None:
        enemy1Orientation = api.getEnemyOrientation()[1][1]
        enemies[1].updateRotation(enemy1Orientation)
    else:
        print "Can't find enemy 0's orientation this tick :("

    if api.getBallCenter() is not None:
        ballPosition =  api.getBallCenter()
        ball.update(Point(ballPosition[0]*X_RATIO,ballPosition[1]*Y_RATIO))
    else:
        print "Shit! Where's the ball gone"

    try:#see who has ball posesion - needs work
        if nearEnough(enemies[0].bearing(ball),enemies[0].currentRotation, near_enough_angle=30) and ball.distance(enemies[0]) < BALL_OWNERSHIP_DISTANCE:
            ball.status = BallStatus.enemyA
        elif nearEnough(enemies[1].bearing(ball),enemies[1].currentRotation, near_enough_angle=30) and  ball.distance(enemies[1]) < BALL_OWNERSHIP_DISTANCE:
            ball.status = BallStatus.enemyB
        elif nearEnough(ally.bearing(ball),ally.currentRotation, near_enough_angle=30) and  ball.distance(ally)< BALL_OWNERSHIP_DISTANCE:
            ball.status = BallStatus.ally
        elif nearEnough(me.bearing(ball), me.currentRotation, near_enough_angle=30) and ball.distance(me)< BALL_OWNERSHIP_DISTANCE and me.grabbed:
            ball.status = BallStatus.me
        # if we can't see it, assume it's the same
        elif api.world['ball_center']==None:
            pass
        # if it's far enough from everything, it's free
        else:
            ball.status = BallStatus.free
    except (TypeError, AttributeError):
        print("Location of some objects unknown")


def tick():
    """Each tick, update your beliefs about the world then decide what action to
    take based on this"""
    updatePositions()
    #Actually_play_ball()
    #playBall()
    #confuseEnemy()
    #shoot()
    #collectBall()
    #receivePass()
    guardGoal()
    threading.Timer(TICK_TIME, tick).start()
    print ball.status

api = WorldApi()

# start it off
if __name__ == "__main__":
    tick()
else:
    updatePositions()
