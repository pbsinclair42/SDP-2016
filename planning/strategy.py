from robotAI import *
from actions import *
from constants import *


def playBall():
    # if we are closest to ball
    ballNearerMeThanAlly = ball.distance(me) > ball.distance(ally)
    ballToEnemyDist = min(ball.distance(enemies[0]), ball.distance(enemies[1]))
    ballNotNearEnemy = ballToEnemyDist < 50
    heldByEnemyA = ball.status == BallStatus.enemyA
    heldByEnemyB = ball.status == BallStatus.enemyB

    if ballNearerMeThanAlly and ballNotNearEnemy:
        print "I'm going to collect the ball."
        collectBall()

    # If the enemy has the ball
    elif heldByEnemyA or heldByEnemyB:
        # if i'm closer to the ball than the ally
        if me.distance(ball) < ally.distance(ball):
            print "I'm going to block a pass"
            blockPass()
        # otherwise, defend the goal
        else:
            print "I'm going to go and guard the goal"
            # move holonomically inside the goal to protect it.
            guardGoal()

    # if we have the ball
    elif ball.status == BallStatus.me:
        # if we can score a goal,
        if lineOfSight(me.currentPoint, opponentGoal):
            print "I'm going to shoot"
            shootBall()
        # else, try and pass to ally
        elif lineOfSight(me.currentPoint, ally.currentPoint):
            print "I'm going to pass to my ally"
            passBall()


# start it off
if __name__ == "__main__":
    playBall()
    tick()
else:
    updatePositions()
