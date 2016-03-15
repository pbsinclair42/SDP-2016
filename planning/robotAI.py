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
#time.sleep(9)
while not api.ready():
    #print "READY BITCH"
    sfgfdgd = 3
print"READY BITCH"
print
try:
    print api.ready()
    print api.world['ally','green']['center']
    print api.world['ally','green']['orientation']
    print api.world['ball_center']
    print api.world['ally','pink']['center']
except:
    print("woops")

def updatePositions():
    # me = 0
    # ally = 1
    # enemyGreen = 2
    # enemyPink = 3
    ALLY_COLOUR = "pink" if OUR_COLOUR == "green" else "green"
    try:
        me.update(Point(api.world['ally',OUR_COLOUR]['center'][0]/2,api.world['ally',OUR_COLOUR]['center'][1]/2))
        me.updateRotation((api.world['ally',OUR_COLOUR]['orientation'][1]))
        print me.currentRotation
    except:
        print "No me to update"
    try:
        ally.update(Point(api.world['ally',ALLY_COLOUR]['center'][0]/2,api.world['ally',ALLY_COLOUR]['center'][1]/2))
        ally.updateRotation((api.world['ally',ALLY_COLOUR]['orientation'][1]))
        print ally.currentRotation
        print "AYE"
    except:
        print "No ally to update"
    try:
        enemyA.update(Point(api.world['enemy',ALLY_COLOUR]['center'][0]/2,api.world['enemy',ALLY_COLOUR]['center'][1]/2))
    except:
        print "No enemy a to update"
    try:
        enenmyB.update(Point(api.world['emeny',OUR_COLOUR]['center'][0]/2,api.world['enemy',OUR_COLOUR]['center'][1]/2))
    except:
        print "No enemy B to update"


    #try:
	print "set ball x"
        ballX = api.world['ball_center'][0]/2
	print "set ball y, the type is " + str(type (ballX))
        ballY = api.world['ball_center'][1]/2

	print "set the global object"
	p = Point(ballX, ballY)
        print "the ball is at " + str(p)
	print "ball is " + str(type(ball))
        ball.update(p)
    #except:

    #    print("no ball update")
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
