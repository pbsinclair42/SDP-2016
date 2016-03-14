import threading
import time
from constants import *
from globalObjects import me, ally, enemies, robots, ball
from helperClasses import BallStatus, Goals, Point
from actions import executePlan
from goals import collectBall, shoot, passBall, receivePass, blockPass, guardGoal
import world
from CommsAPI import commsSystem

api = world.WorldApi()
time.sleep(9)
try:
    print api.world['ally','green']['center']
    print api.world['ally','green']['orientation']
    print api.world['ball_center']
except:
    print("woops")

def updatePositions():
    # me = 0
    # ally = 1
    # enemyGreen = 2
    # enemyPink = 3
    groups = ["ally", "enemy"]
    TEAM_MATE_COLOUR = "pink" if OUR_COLOUR == "green" else "green"
    robots_colours = [OUR_COLOUR, TEAM_MATE_COLOUR]
    i = 0
    for group in groups:
        # When setting enemies, the order of colours is important.
        if i > 2:
            robots_colours = ["pink", "green"]
        for robot in robots_colours:
            try:
                r = api.world[group, robot]['center']
                p = Point(r[0], r[1])
                print("group " + group + " robot " + robot + " i " + str(i) + str(type(p)) )
                robots[i].updateRotation(api.world[group, robot]['orientation'][0])
                print (api.world[group, robot]['orientation'] +90)
                print "My colour is: Robot[0].name" + robots[i].name
                robots[i].update(p)
            except (TypeError):
                pass
            i += 1
    try:
        ball.update(Point(api.world['ball_center'][0],api.world['ball_center'][1]))
    except:
        print("no ball update")
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
        elif Point(api.world['ball_center'][0],api.world['ball_center'][1]) !=None:
            ball.status = BallStatus.free
    except (TypeError, AttributeError):
        print("Location of some objects unknown")

    # check whether the last command sent has been finished or not
    if commsSystem.am_i_done():
        me.moving=False



def makePlan():
    """Decide what to do based on the system's current
    beliefs about the state of play"""
    if me.goal == Goals.none:
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
            sys.exit()


def tick():
    """Each tick, update your beliefs about the world then decide what action to
    take based on this"""
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
