from robotAI import *


def playBall():
    if(ball.distance(me) > (ball.distance(ally) and ball.distance(enemies[0]) and ball.distance(enemies[1]))):#if we are closest to ball
        collectBall()
    elif(ball.status == (BallStatus.enemyA or Ballstatus.enemyB)):
        if( me.distance(ball) < ally.distance(ball)):#if i'm closer to the ball than the ally
            blockPass()
        else:#defend the goal
            guardGoal()
    elif(ball.status == BallStatus.me):#if we have the ball
        if(lineOfSight(me.currentPoint,opponentGoal) == False):#if we can score a goal,
            shootBall()
        elif(lineOfSight(me.currentPoint,ally.currentPoint) == False):#else, try and pass to ally
            passBall()

