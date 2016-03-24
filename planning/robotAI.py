import threading

from constants import *
from globalObjects import me, ally, enemies, robots, ball
from helperClasses import BallStatus, Goals, Point
from actions import executePlan
from goals import collectBall, shoot, passBall, receivePass, blockPass, guardGoal
from strategy import playBall
import world
from CommsAPI import commsSystem


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
        AllyPosition = api.getAllyPosition()
        AllyOrientation = api.getAllyOrientation()[1]
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
        print "Enemy_0 Position: ", api.getEnemyPositions()[1]

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

    # check whether the last command sent has been finished or not
    if commsSystem.am_i_done():
        me.moving=False


def makePlan():
    """DEPRECATED
    
    Explicitly tell the robot what to do"""

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
    playBall()
    executePlan()
    print ball.status
    threading.Timer(TICK_TIME, tick).start()

# start it off
if __name__ == "__main__":
    tick()
else:
    updatePositions()
