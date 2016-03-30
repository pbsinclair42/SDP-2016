from constants import *
from globalObjects import me, ally, ball, enemies, ourGoal, opponentGoal
from helperClasses import Point, Goals, BallStatus
from helperFunctions import tan, nearEnough, lineOfSight
import sys
import random
sys.path.append(ROOT_DIR+'comms/')
from RobotController import RobotController


controller = RobotController()

def collectBall():
    me.goals = Goals.collectBall
    """Move towards then grab the ball"""
    # if we don't yet have the ball, go get it!
    if ball.status != BallStatus.me:
        angle_to_face = me.bearing(ball)
        angle_to_move = angle_to_face
        distance_to_move = me.distance(ball)
        controller.move(angle_to_face,angle_to_move,distance_to_move,True)
    else:
        if not controller.stopped:
            controller.stop_robot()
        if not controller.grabbed:
            controller.grab(False)
        me.goals = Goals.collectBall
    # if we've got it, we're done
    #else:
    #    print "We already have the ball, you fool"
    #    #controller.stop_robot()


def shoot():
    """Kick the ball full power towards the goal"""
    angle_to_face = me.bearing(opponentGoal)
    print "angle to face: ", angle_to_face, controller.absolute_to_magnetic(angle_to_face)
    if not controller.kickflag:
    # if we're facing the goal, shoot!
        controller.move(angle_to_face,0,0,False,rotate_in_place=True)
        controller.kick(255)
    """me.plan = [{'action': Actions.rotateToAngle, 'targetFunction': aim},
               {'action': Actions.kick, 'targetFunction': distanceToKick}]"""


def passBall():
    """Kick the ball full power towards the goal"""
    angle_to_face = me.bearing(ally)
    print "angle to face: ", angle_to_face, controller.absolute_to_magnetic(angle_to_face)
    if not controller.kickflag:
    # if we're facing the goal, shoot!
        controller.move(angle_to_face,0,0,False,rotate_in_place=True)
        controller.kick(255)


    """me.plan = [{'action': Actions.rotateToAngle, 'targetFunction': rotate},
               {'action': Actions.kick, 'targetFunction': kickToAlly}]"""


def receivePass():
    #TODO
    me.goal = Goals.recievePass
    ball_distance = me.distance(ball)
    angle_to_ball = me.bearing(ball)
    angle_to_face = me.bearing(ally)
    if ball.status != BallStatus.free:
        controller.ungrab(True)
        controller.move(angle_to_face, None, ball_distance, True, True)
    elif ball.status == BallStatus.me:
        controller.grab(True)
        controller.stop_robot()
        me.goals = Goals.none
    else:
        controller.move(angle_to_ball,angle_to_ball,ball_distance,True)



def blockPass():
    #me.goals = Goals.BlockPass
    e0 = enemies[0].currentPoint
    e1 = enemies[1].currentPoint
    def blockHere():
        """move to inbetween two oponents"""
        x = (e0.x + e1.x)/2
        y = (e0.y + e1.y)/2
        return Point(x, y)

    point_to_be = blockHere()
    angle_to_face = me.bearing(ball)
    angle_to_move = me.bearing(point_to_be)
    distance = me.distance(point_to_be)
    if lineOfSight(e0,e1) == True:
        controller.move(angle_to_face,angle_to_move,distance)
    else:
        me.goals = Goals.none
        if ball.status == enemyA:#move to enemyB
            move_to_b = me.bearing(e1)
            dist_to_b = me.distance(e1)
            controller.move(angle_to_face,move_to_b,(dist_to_b/2))
        else:#move to enemyA
            move_to_a = me.bearing(e0)
            dist_to_a = me.distance(e0)
            controller.move(angle_to_face,move_to_a,(dist_to_a/2))



def confuseEnemy():
    """Shoogle around a bit to confuse the enemy and hopefully make them move"""
    angle_to_face = me.currentRotation
    angle_to_move = random.uniform(0,180)
    distance = 20
    controller.move(angle_to_face,angle_to_move,distance)
    # save the plan to the robot


def guardGoal():#Little faith in this
    """Stop bad people from scoring"""
    me.goals = Goals.guardGoal
    angle_to_face = me.bearing(ball)
    # Krassy: We need an FSM here. One part for going to the ball and stopping if near enough,
    # Krassy: one part for moving to defensive point and stopping if near enough
    # Krassy: one part for handling when they've kicked
    # if we're on our goal line, move to block the ball
    if 5 <= abs(me.currentPoint.x - ourGoal.x) <= 15:
        #controller.grab(True)
        #controller.stop_robot()
        # work out which enemy has the ball
        if ball.status == BallStatus.enemyA:
            enemyNum=0
        else:
            enemyNum=1

        # calculate where on the y axis the ball would hit if kicked now
        x_dist = enemies[enemyNum].currentPoint.x  - ourGoal.x
        y_dist = x_dist * tan(enemies[enemyNum].currentRotation)
        y_intersection = enemies[enemyNum].currentPoint.x - y_dist

        # calculate where we should therefore go to (we don't want to leave the goal line)
        minY = PITCH_WIDTH/2 - 0.5*GOAL_WIDTH + ROBOT_WIDTH/2
        maxY = PITCH_WIDTH/2 + 0.5*GOAL_WIDTH - ROBOT_WIDTH/2
        point_to_be = Point(ourGoal.x, max(minY, min(maxY, y_intersection)))

        # calculate the paramaters to send to the robot
        distance = me.distance(point_to_be)
        # we want to move holonomically up and down
        if point_to_be.y<me.currentPoint.y:
            angle_to_move = 90
        else:
            angle_to_move = 270
        controller.move(angle_to_face,angle_to_move,distance)
        me.goals = Goals.none
    else:
        # if not in on our goal line, move into the middle of it
        angle_to_move = me.bearing(ourGoal)
        distance = me.distance(ourGoal)
        controller.move(angle_to_move,angle_to_move,distance)


def clearPlan():
    """Reset the robot's goal and plan"""
    # TODO
    """
    me.goal=Goals.none
    print("GOAL CLEAED")
    """
