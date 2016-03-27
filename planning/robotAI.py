import threading
import time
from constants import *
from globalObjects import me, ally, enemies, robots, ball
from helperClasses import BallStatus, Goals, Point
#from actions import executePlan
from goals_new import collectBall, shoot, passBall, receivePass, blockPass, guardGoal
import world
#from CommsAPI import commsSystem
from RobotController import RobotController as controller
def updatePositions():
    # me = 0
    # ally = 1
    # enemyGreen = 2
    # enemyPink = 3

    if api.getMyPosition() is not None:
        mePosition = api.getMyPosition()
        meOrientation = api.getMyOrientation()[1]
        me.update(Point(mePosition[0],mePosition[1]))
    else :
        print "Can't find me this tick :("
    if api.getAllyPosition() is not None:
        try:
            AllyPosition = api.getAllyPosition()
            AllyOrientation = api.getAllyOrientation()[1]
            ally.update(Point(allyPosition[0],allyPosition[1]))
        except:
            print "ally don't exist"
    else:
        print "Can't find my friend this tick :("
    if api.getEnemyPositions()[0] is not None:
        try:
            enemy0Position = api.getEnemyPositions()[0]
            emeny0Orientation =  api.getEnemyOrientation()[0][1]
            ememyA.update(Point(enemy0Position[0],enemy0Position[1]))
        except:
            print "enemy1 don't exist"
    else:
        print "Can't find enemy 0 this tick :("
    if api.getEnemyPositions()[1] is not None:
        try:
            enemy1Position = api.getEnemyPositions()[1]
            enemy1Orientation = api.getEnemyOrientation()[1][1]
            enemyB.update(Point(enemy1Position[0],enemy1Position[1]))
        except:
            print "enemy2 don't exist"
    else:
        print "Enemy_0 Position: ", api.getEnemyPositions()[1]
    if api.getBallCenter() is not None:
        ballPosition =  api.getBallCenter()
        ball.update(Point(ballPosition[0],ballPosition[1]))
    else:
        print "Shit! Where's the ball gone"
    try:#see who has ball posesion - needs work
        if enemies[0].bearing(ball) == enemies[0].currentRotation and ball.distance(enemies[0]) < BALL_OWNERSHIP_DISTANCE:
            ball.status = BallStatus.enemyA
        elif  enemies[1].bearing(ball) == enemies[1].currentRotation and ball.distance(enemies[1]) < BALL_OWNERSHIP_DISTANCE:
            ball.status = BallStatus.enemyB
        elif  ally.bearing(ball) == ally.currentRotation and ball.distance(ally)< BALL_OWNERSHIP_DISTANCE:
            ball.status = BallStatus.ally
        elif me.bearing(ball) == me.currentRotation and ball.distance(me)< BALL_OWNERSHIP_DISTANCE and me.grabbed:
            ball.status = BallStatus.me
        # if we can't see it, assume it's the same, otherwise if it's far enough from everything, it's free
        elif Point(api.world['ball_center'][0],api.world['ball_center'][1]) !=None:
            ball.status = BallStatus.free
    except (TypeError, AttributeError):
        print("Location of some objects unknown")

    # check whether the last command sent has been finished or not
    #if commsSystem.am_i_done():
    #    me.moving=False



def makePlan():
    """Decide what to do based on the system's current
    beliefs about the state of play"""
    collectBall()
    """if me.goal == Goals.none:
        if not USING_SIMULATOR:
            commsSystem.restart()
        action = "0"
        while action not in ['1', '2', '3', '4', '5', '6', '7', '8']:
            print("What action should I do now?")
            action = raw_input("1. Collect ball\n2. Shoot ball\n3. Pass ball\n4. Recieve ball\n5. Block pass\n6. Guard Goal\n7. Stop\n? ")
        if action == "1":
            collectBall()
        elif action == "2":
            shoot()
        elif action == "3":
            passBall()
        elif action == "4":
            receivePass()
        elif action == "5":
            blockPass()
        elif action == "6":
            guardGoal()
        else:
            import sys
            sys.exit()"""


def tick():
    """Each tick, update your beliefs about the world then decide what action to
    take based on this"""
    # if currently simulating, update the simulation
    if USING_SIMULATOR:
        commsSystem.tick()
    updatePositions()
    makePlan()
    #executePlan()
    threading.Timer(TICK_TIME, tick).start()

# start it off
if __name__ == "__main__":
    api = world.WorldApi()
    tick()
else:
    updatePositions()
