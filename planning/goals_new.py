from constants import *
from globalObjects import me, ally, ball, enemies, ourGoal, opponentGoal
from helperClasses import Point, Goals, BallStatus
from helperFunctions import tan, nearEnough
import sys
sys.path.append(ROOT_DIR+'comms/')
from RobotController import RobotController

controller = RobotController()

def collectBall():
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
    # if we've got it, we're done
    #else:
    #    print "We already have the ball, you fool"
    #    #controller.stop_robot()


def shoot():
    """Kick the ball full power towards the goal"""
    angle_to_face = me.bearing(opponentGoal)
    if not controller.kickflag:
    # if we're facing the goal, shoot!
        controller.move(angle_to_face,0,0,False,rotate_in_place=True)
        controller.kick(255)
    """me.plan = [{'action': Actions.rotateToAngle, 'targetFunction': aim},
               {'action': Actions.kick, 'targetFunction': distanceToKick}]"""


def passBall():
    angle_to_face = ally.bearing(me)#Not 100% convinced on this bearing
    print "angle to face: ", angle_to_face, controller.absolute_to_magnetic(angle_to_face)
    if not controller.kickflag:
        controller.move(angle_to_face,None,None, None, True)
        controller.kick(255)
        

    """me.plan = [{'action': Actions.rotateToAngle, 'targetFunction': rotate},
               {'action': Actions.kick, 'targetFunction': kickToAlly}]"""


def receivePass():
    #TODO
    """
    me.goal = Goals.receivePass

    def rotate():
        return me.bearing(ally)

    me.plan = [{'action': Actions.rotateToAngle, 'targetFunction': rotate},
               {'action': Actions.ungrab},
               {'action': Actions.receiveBall},
               {'action': Actions.grab}]
               """


def blockPass():

    def blockHere():
        """move to inbetween two oponents"""
        e0 = enemies[0].currentPoint
        e1 = enemies[1].currentPoint
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
        if ball.status == enemyA:#move to enemyB
            move_to_b = me.bearing(e1)
            dist_to_b = me.distance(e1)
            controller.move(angle_to_face,move_to_b,dist_to_b)
        else:#move to enemyA
            move_to_a = me.bearing(e0)
            dist_to_a = me.distance(e0)
            controller.move(angle_to_face,move_to_a,dist_to_a)

    """me.plan = [{'action': Actions.moveToPoint, 'targetFunction': blockHere},
               {'action': Actions.rotateToAngle, 'targetFunction': rotate},
               {'action': Actions.ungrab},
               {'action': Actions.receiveBall},
               {'action': Actions.grab}]"""


def confuseEnemy():
    """Shoogle around a bit to confuse the enemy and hopefully make them move"""
    # TODO
    # save the plan to the robot
    """
    me.goal = Goals.confuse
    print("NEW GOAL: Confuse the enemy")

    actualDirection = me.currentRotation
    randomRotationAmount = randrange(20,90)

    def firstRotationAmount():
        return actualDirection + randomRotationAmount

    def backAgain():
        return actualDirection

    me.plan = [{'action': Actions.rotateToAngle, 'targetFunction': firstRotationAmount},
               {'action': Actions.rotateToAngle, 'targetFunction': backAgain}]
    """


def guardGoal():#Little faith in this
    """Stop bad people from scoring"""
    angle_to_face = me.bearing(ball)

    # if we're on our goal line, move to block the ball
    if abs(me.currentPoint.x - ourGoal.x) <= ITLL_DO_POINT:
        controller.grab(True)
        controller.stop_robot()
        """# work out which enemy has the ball
        if ball.status == enemyA:
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

        controller.move(angle_to_face,angle_to_move,distance)"""
    else:
        # if not in on our goal line, move into the middle of it
        angle_to_move = me.bearing(ourGoal)
        distance = me.distance(ourGoal)
        controller.move(angle_to_mave,angle_to_move,distance)


def clearPlan():
    """Reset the robot's goal and plan"""
    # TODO
    """
    me.goal=Goals.none
    print("GOAL CLEAED")
    """
