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
    """Move towards then grab the ball"""
    angle_to_face = me.bearing(ball)
    angle_to_move = angle_to_face
    distance_to_move = me.distance(ball)
    controller.move(angle_to_face,angle_to_move,distance_to_move,True)


def shoot():
    """Kick the ball full power towards the goal"""
    angle_to_face = me.bearing(opponentGoal)
    # if we're facing the goal, shoot!
    if nearEnough(angle_to_face, me.currentRotation):
        controller.kick(255)
    # otherwise, turn to face the goal
    else:
        controller.move(angle_to_face,0,0,False,rotate_in_place=True)


def passBall():
    """Kick the ball full power towards our ally"""
    angle_to_face = me.bearing(ally)
    # if we're facing the ally, pass them the ball
    if nearEnough(angle_to_face, me.currentRotation):
        controller.kick(255)
    # otherwise, turn to face our ally
    else:
        controller.move(angle_to_face,0,0,False,rotate_in_place=True)


def receivePass():
    """Face our ally and get ready to grab the ball if they kick it to us"""
    angle_to_face = me.bearing(ally)
    # if we're facing the ally, ungrab and get ready to receive the ball
    if nearEnough(angle_to_face, me.currentRotation):
        controller.ungrab(True)
    # otherwise, turn to face our ally
    else:
        controller.move(angle_to_face,0,0,False,rotate_in_place=True)


def blockPass():
    """Move to inbetween the two enemies"""
    # work out where to move to
    e0 = enemies[0].currentPoint
    e1 = enemies[1].currentPoint
    x = (e0.x + e1.x)/2
    y = (e0.y + e1.y)/2
    point_to_be = Point(x, y)

    # work out the parameters for the move command
    angle_to_face = point_to_be.bearing(ball.currentPoint)
    angle_to_move = me.bearing(point_to_be)
    distance = me.distance(point_to_be)
    controller.move(angle_to_face,angle_to_move,distance)


def confuseEnemy():
    """Shoogle around a bit to confuse the enemy and hopefully make them move"""
    angle_to_face = me.currentRotation
    angle_to_face += random.uniform(-60,60)
    controller.move(angle_to_face,0,0,False,rotate_in_place=True)


def guardGoal():
    """Go to the goal line and face the enemy with the ball"""
    me.goals = Goals.guardGoal
    angle_to_face = me.bearing(ball)

    # if we're on our goal line, move to block the ball
    if abs(me.currentPoint.x - ourGoal.x) <= 15:
        # work out which enemy has the ball
        if ball.status == BallStatus.enemyA:
            enemyNum=0
        elif ball.status == BallStatus.enemyB:
            enemyNum=1
        else:
            print("They don't have the ball you dafty")
            controller.stop_robot()
            return

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
    controller.stop_robot()
    