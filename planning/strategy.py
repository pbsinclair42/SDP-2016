from globalObjects import ball, me, ally, enemies, ourGoal, opponentGoal, lineOfSight
from helperClasses import BallStatus, Goals
from helperFunctions import isEnemyBox, isOurBoxFree
from goals_new import collectBall, blockPass, guardGoal, shoot, passBall, confuseEnemy, receivePass, clearPlan
from constants import *


def playBall():
    # if we are closest to ball
    heldByMe = ball.status == BallStatus.me
    heldByAlly = ball.status == BallStatus.ally
    heldByEnemyA = ball.status == BallStatus.enemyA
    heldByEnemyB = ball.status == BallStatus.enemyB
    ballFree = ball.status == BallStatus.free

    # If the enemy has the ball
    if heldByEnemyA or heldByEnemyB:
        # if I'm closer to our goal than the ally, go defend it
        if me.distance(ourGoal) < ally.distance(ourGoal):
            guardGoal()
        # otherwise, intercept the pass
        else:
            blockPass()

    # if we have the ball
    elif heldByMe:
        # shoot if possible
        if lineOfSight(me.currentPoint, opponentGoal):
            shoot()
        # else, try and pass to ally
        elif lineOfSight(me.currentPoint, ally.currentPoint):
            passBall()
        else:
            confuseEnemy()

    # if our ally has the ball, set up a pass
    elif ball.status == BallStatus.ally:
        receivePass()

    # if noone has the ball, go grab the ball or defend
    elif me.distance(ball) < ally.distance(ball) and not isEnemyBox(ball.currentPoint):
        collectBall()
    else:
        guardGoal()
