from robotAI import *


def playBall():
    # if we are closest to ball
    ballNearerMeThanAlly = ball.distance(me) > ball.distance(ally)
    ballToEnemyDist = min(ball.distance(enemies[0]), ball.distance(enemies[1]))
    ballNotNearEnemy = ballToEnemyDist < 50
    heldByEnemyA = ball.status == BallStatus.enemyA
    heldByEnemyB = ball.status == BallStatus.enemyB

    if ballNearerMeThanAlly and ballNotNearEnemy:
        collectBall()

    # If the enemy has the ball
    elif heldByEnemyA or heldByEnemyB:
        # if i'm closer to the ball than the ally
        if me.distance(ball) < ally.distance(ball):
            blockPass()
        # otherwise, defend the goal
        else:
            guardGoal()

    # if we have the ball
    elif ball.status == BallStatus.me:
        # if we can score a goal,
        if lineOfSight(me.currentPoint, opponentGoal) == False:
            shootBall()
        # else, try and pass to ally
        elif lineOfSight(me.currentPoint, ally.currentPoint) == False:
            passBall()

if __name__ == '__main__':
    playBall()
