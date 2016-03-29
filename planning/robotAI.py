import threading

from constants import *
from globalObjects import me, ally, enemies, ball
from helperClasses import BallStatus, Goals, Point
from goals_new import collectBall, shoot, passBall, receivePass, blockPass, guardGoal
from helperFunctions import nearEnough
from strategy import playBall
from world import WorldApi

def updatePositions():
    """Updates the system's belief of the state of the game based on the vision system"""
    # get the info on the robots from the vision system
    if api.getMyPosition() is not None:
        mePosition = api.getMyPosition()
        # may crash if we can get our position but not orientation?
        meOrientation = api.getMyOrientation()[1]
        me.update(Point(mePosition[0],mePosition[1]))
        me.updateRotation(meOrientation)
    else:
        print "Can't find me this tick :("

    if api.getAllyPosition() is not None:
        allyPosition = api.getAllyPosition()
        allyOrientation = api.getAllyOrientation()[1]
        ally.update(Point(allyPosition[0],allyPosition[1]))
        ally.updateRotation(allyOrientation)
    else:
        print "Can't find my friend this tick :("

    if api.getEnemyPositions()[0] is not None:
        enemy0Position = api.getEnemyPositions()[0]
        emeny0Orientation =  api.getEnemyOrientation()[0][1]
        enemies[0].update(Point(enemy0Position[0],enemy0Position[1]))
        enemies[0].updateRotation(emeny0Orientation)
    else:
        print "Can't find enemy 0 this tick :("

    if api.getEnemyPositions()[1] is not None:
        enemy1Position = api.getEnemyPositions()[1]
        enemy1Orientation = api.getEnemyOrientation()[1][1]
        enemies[1].update(Point(enemy1Position[0],enemy1Position[1]))
        enemies[1].updateRotation(enemy1Orientation)
    else:
        print "Can't find enemy 1 this tick :("

    if api.getBallCenter() is not None:
        ballPosition =  api.getBallCenter()
        ball.update(Point(ballPosition[0],ballPosition[1]))
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
    #playBall()
    collectBall()
    threading.Timer(TICK_TIME, tick).start()

api = WorldApi()

# start it off
if __name__ == "__main__":
    tick()
else:
    updatePositions()
