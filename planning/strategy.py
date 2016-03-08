from robotAI import *


def playBall():
    """
    if we are closest to the ball, go get it
    if the enemy has the ball and we are near goal, go to goal
        else, try and intercept
    if we have ball and can shoot, do so
        else pass to teammate
            side note, can we move with the ball


    """
    if(ball.distance(me) > (ball.distance(ally) and ball.distance(enemies[0]) and ball.distance(enemies[1]))):#if we are closest to ball
        collectBall()
    elif(ball.status == (BallStatus.enemyA or Ballstatus.enemyB)):
        if( me.distance(ball) < ally.distance(ball)):#if i'm closer to the ball than the ally
            blockPass()
        else:#defend the goal
            guardGoal()
    elif(ball.status == BallStatus.me):#if we have the ball
        if(me.distance(ourGoal) < 50):#if we can score a goal, TODO change it so it checks if we have a clear shot
            shootBall()
        else:#else, try and pass to ally
            passBall()
