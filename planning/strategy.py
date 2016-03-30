from globalObjects import ball, me, ally, enemies, ourGoal, opponentGoal
from helperClasses import BallStatus, Goals
from goals_new import collectBall, blockPass, guardGoal, shoot, passBall, confuseEnemy, receivePass, clearPlan
from helperFunctions import lineOfSight
from constants import *


def playBall():
    # if we are closest to ball
    ballNearerMeThanAlly = ball.distance(me) > ball.distance(ally)
    ballToEnemyDist = min(ball.distance(enemies[0]), ball.distance(enemies[1]))
    ballNotNearEnemy = ballToEnemyDist < 50
    heldByEnemyA = ball.status == BallStatus.enemyA
    heldByEnemyB = ball.status == BallStatus.enemyB
    ballFree = ball.status == BallStatus.free

    # stop guarding the goal if you could be more useful elsewhere
    if me.goal == Goals.guardGoal:
        if not (heldByEnemyA or heldByEnemyB or (ball.status == BallStatus.free and not ballNearerMeThanAlly)) :
            clearPlan()

    elif me.goal == Goals.collectBall:
        if heldByEnemyA or heldByEnemyB or ball.status==BallStatus.ally:
            clearPlan()

    if me.goal == Goals.none:
        # If the enemy has the ball
        if heldByEnemyA or heldByEnemyB:
            # if I'm closer to the ball than the ally
            if me.distance(ball) < ally.distance(ball):
                blockPass()
            # otherwise, defend the goal
            else:
                guardGoal()

        # if we have the ball
        elif ball.status == BallStatus.me:
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
        else:
            collectBall()
        #else:
        #    guardGoal()

def Actually_play_ball():
    print ball.status
    ballNearerMeThanAlly = ball.distance(me) < ball.distance(ally)
    ballToEnemyDist = min(ball.distance(enemies[0]), ball.distance(enemies[1]))
    ballNotNearEnemy = ballToEnemyDist < 50
    heldByEnemyA = ball.status == BallStatus.enemyA
    heldByEnemyB = ball.status == BallStatus.enemyB
    ballFree = ball.status == BallStatus.free

    if heldByEnemyA or heldByEnemyB:
        # if I'm closer to the ball than the ally
        if me.distance(ball) < ally.distance(ball):
            blockPass()
        # otherwise, defend the goal
        elif lineOfSight(me.currentPoint,ourGoal):
            guardGoal()
        else:
            confuseEnemy()

    # if we have the ball
    elif ball.status == BallStatus.me:
        # shoot if possible
        if lineOfSight(me.currentPoint, opponentGoal):
            shoot()
        # else, try and pass to ally
        elif lineOfSight(me.currentPoint, ally.currentPoint):
            passBall()
        #else:
        #    confuseEnemy()

    # if our ally has the ball, set up a pass
    elif ball.status == BallStatus.ally:
        receivePass()

    # if noone has the ball, go grab the ball or defend
    elif ballFree and ballNearerMeThanAlly:
        collectBall()
    #else:
    #    print "SHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
    #    print ball.status
        #guardGoal()
    #    confuseEnemy()

