from enum import Enum
from constants import *
from helperClasses import Point, BallStatus
from helperFunctions import sin, cos
from moveables import Robot, Ball

# our supreme robot
simulatedMe = Robot(name="simulatedMe")
# Team 3's robot
simulatedAlly = Robot(name="simulatedAlly")
# the two robots we're against
simulatedEnemies = [Robot(name="simulatedPinkEnemy"), Robot(name="simulatedGreenEnemy")]
# a list containing all robots on the field for convenience
simulatedRobots = [simulatedMe, simulatedAlly]+simulatedEnemies
# guess what this could possibly be
simulatedBall = Ball(name="simulatedBall")


class Simulator(object):

    def __init__(self, debug=False):
        self.currentActionQueue=[]
        self.grabbed=True
        self.holdingBall=False
        self.current_cmd = 0
        simulatedStart(Point(50,50), Point(200,25), Point(166,211), Point(52,102), 15, 38, 150, -62, Point(100,100), BallStatus.free)
        # since we're using a simulator, set the fact that we know where we are exactly at all times
        POINT_ACCURACY = 0.1
        ANGLE_ACCURACY = 0.1


    # move holonomically at an angle of `degrees` anticlockwise and a distance of `distance` cm
    def holo(self,degrees,distance):
        checkValid(degrees,distance)
        # TODO
        pass

    # move holonomically at an angle of `degrees` clockwise and a distance of `distance` cm
    def holoneg(self,degrees,distance):
        checkValid(degrees,distance)
        # TODO
        pass

    # stop all motors
    def stop(self):
        self.currentActionQueue=[]

    # rotate `degrees` degrees anticlockwise, then move `distance` cm
    def rotate(self,distance,degrees):
        checkValid(degrees,distance)
        if degrees>0:
            self.currentActionQueue.append({'action': SimulatorActions.rotate, 'amount': degrees, 'timeLeft': degrees/MAX_ROT_SPEED})
        if distance>0:
            self.currentActionQueue.append({'action': SimulatorActions.moveForwards, 'amount': distance, 'timeLeft': distance/MAX_SPEED})
    # rotate `degrees` degrees clockwise, then move `distance` cm
    def rotateneg(self,distance,degrees):
        checkValid(degrees,distance)
        if degrees>0:
            self.currentActionQueue.append({'action': SimulatorActions.rotate, 'amount': -degrees, 'timeLeft': degrees/MAX_ROT_SPEED})
        if distance>0:
            self.currentActionQueue.append({'action': SimulatorActions.moveForwards, 'amount': distance, 'timeLeft': distance/MAX_SPEED})
    # kick with power `distance`
    def kick(self,distance):
        checkValid(distance)
        self.currentActionQueue.append({'action': SimulatorActions.ungrab, 'timeLeft': UNGRAB_TIME})
        self.currentActionQueue.append({'action': SimulatorActions.kick, 'amount': distance, 'timeLeft': KICK_TIME})
        self.currentActionQueue.append({'action': SimulatorActions.grab, 'timeLeft': GRAB_TIME})

    # cancel previous command and any queued commands
    def flush(self):
        self.currentActionQueue=[]

    # grab the ball
    # ensure the grabber is opened before calling!
    def grab(self):
        self.currentActionQueue.append({'action': SimulatorActions.grab, 'timeLeft': GRAB_TIME})

    # open the grabber, ready to grab
    def ungrab(self):
        self.currentActionQueue.append({'action': SimulatorActions.ungrab, 'timeLeft': UNGRAB_TIME})

    def tick(self, tickTimeLeft=TICK_TIME):
        '''Update the status of our robot and the ball based on our recent actions

        tickTimeLeft:   the time remaining before the next tick, TICK_TIME by default
                        or slightly less than this if an action finishes halfway through a tick
                        and this gets called again on the remaining time'''
        try:
            currentAction = self.currentActionQueue[0]
        except IndexError:
            # if it's not currently carrying out an action, it'll stay the same
            return
        # if currently moving forwards
        if currentAction['action']==SimulatorActions.moveForwards:
            # if it'll keep going for this whole tick, move the simulated robot forwards the appropriate amount
            if TICK_TIME<currentAction['timeLeft']:
                currentAction['timeLeft']-=TICK_TIME
                distanceTravelled = MAX_SPEED*TICK_TIME
                angle = simulatedMe.currentRotation
                xDisplacement = round(cos(angle)*distanceTravelled, 2)
                yDisplacement = -round(sin(angle)*distanceTravelled, 2)
                simulatedMe.currentPoint = Point(simulatedMe.currentPoint.x+xDisplacement, simulatedMe.currentPoint.y+yDisplacement)
            # if not, move the simulated robot forwards the lesser amount, then start the next action in the queue with the remaining time
            else:
                tickTimeLeft = TICK_TIME-currentAction['timeLeft']
                distanceTravelled = MAX_SPEED*currentAction['timeLeft']
                angle = simulatedMe.currentRotation
                xDisplacement = round(cos(angle)*distanceTravelled, 2)
                yDisplacement = -round(sin(angle)*distanceTravelled, 2)
                simulatedMe.currentPoint = Point(simulatedMe.currentPoint.x+xDisplacement, simulatedMe.currentPoint.y+yDisplacement)
                # report that we've finished executing this command
                self.currentActionQueue.pop(0)
                self.current_cmd +=1
                # start the next action if it's queued
                self.tick(tickTimeLeft)

        # if currently rotating
        elif currentAction['action']==SimulatorActions.rotate:
            # if it'll keep going for this whole tick, turn the simulated robot forwards the appropriate amount
            if TICK_TIME<currentAction['timeLeft']:
                # calculate how far to turn
                currentAction['timeLeft']-=TICK_TIME
                degreesTurned = MAX_ROT_SPEED*TICK_TIME
                # turn the right direction
                if currentAction['amount']<0:
                    simulatedMe.currentRotation -= degreesTurned
                else:
                    simulatedMe.currentRotation += degreesTurned
                # keep the value in [-180, 180]
                if simulatedMe.currentRotation<-180:
                    simulatedMe.currentRotation+=360
                elif simulatedMe.currentRotation>180:
                    simulatedMe.currentRotation-=360

            # if not, move the simulated robot forwards the lesser amount, then start the next action in the queue with the remaining time
            else:
                # calculate how far to turn
                tickTimeLeft = TICK_TIME-currentAction['timeLeft']
                degreesTurned = MAX_ROT_SPEED*currentAction['timeLeft']
                # turn the right direction
                if currentAction['amount']<0:
                    simulatedMe.currentRotation -= degreesTurned
                else:
                    simulatedMe.currentRotation += degreesTurned
                # keep the value in [-180, 180]
                if simulatedMe.currentRotation<-180:
                    simulatedMe.currentRotation+=360
                elif simulatedMe.currentRotation>180:
                    simulatedMe.currentRotation-=360
                # report that we've finished executing this command
                self.currentActionQueue.pop(0)
                self.current_cmd +=1
                # start the next action if it's queued
                self.tick(tickTimeLeft)

        # if currently kicking
        elif currentAction['action']==SimulatorActions.kick:
            # if it'll keep kicking for this whole tick, the only potential change is that the ball starts moving
            if TICK_TIME<currentAction['timeLeft']:
                currentAction['timeLeft']-=TICK_TIME
                # TODO start the ball moving at the appropriate point

            # if not, start the next action in the queue with the remaining time
            else:
                tickTimeLeft = TICK_TIME-currentAction['timeLeft']
                # report that we've finished executing this command
                self.currentActionQueue.pop(0)
                self.current_cmd +=1
                # start the next action if it's queued
                self.tick(tickTimeLeft)

        # if currently grabbing
        elif currentAction['action']==SimulatorActions.grab:
            # if it'll keep grabbing for this whole tick, the only potential change is that the ball stops moving
            if TICK_TIME<currentAction['timeLeft']:
                currentAction['timeLeft']-=TICK_TIME
                # TODO potentially stop the ball and toggle 'holding ball' state

            # if not, start the next action in the queue with the remaining time
            else:
                self.grabbed=True
                tickTimeLeft = TICK_TIME-currentAction['timeLeft']
                # report that we've finished executing this command
                self.currentActionQueue.pop(0)
                self.current_cmd +=1
                # start the next action if it's queued
                self.tick(tickTimeLeft)

        # if currently ungrabbing
        elif currentAction['action']==SimulatorActions.ungrab:
            # if it'll keep grabbing for this whole tick, nothing changes
            if TICK_TIME<currentAction['timeLeft']:
                currentAction['timeLeft']-=TICK_TIME

            # if not, start the next action in the queue with the remaining time
            else:
                self.grabbed=False
                tickTimeLeft = TICK_TIME-currentAction['timeLeft']
                # report that we've finished executing this command
                self.currentActionQueue.pop(0)
                self.current_cmd +=1
                # start the next action if it's queued
                self.tick(tickTimeLeft)


def simulatedStart(myPoint, allyPoint, enemyAPoint, enemyBPoint, myRot, allyRot, enemyARot, enemyBRot, ballPoint, ballStat):
    '''Reset the status of all robots and the ball'''
    # reset all robots/balls
    simulatedMe.__init__()
    simulatedAlly.__init__()
    simulatedEnemies[0].__init__()
    simulatedEnemies[1].__init__()
    simulatedBall.__init__()
    # update them with the inputted points
    simulatedMe.update(myPoint)
    simulatedMe.updateRotation(myRot)
    simulatedAlly.update(allyPoint)
    simulatedAlly.updateRotation(allyRot)
    simulatedEnemies[0].update(enemyAPoint)
    simulatedEnemies[0].updateRotation(enemyARot)
    simulatedEnemies[1].update(enemyBPoint)
    simulatedEnemies[1].updateRotation(enemyBRot)
    simulatedBall.update(ballPoint)
    simulatedBall.status = ballStat


def checkValid(*toCheck):
    '''Ensure all the parameters inputted are valid bytes'''
    for x in toCheck:
        if x>255 or x<0 or x!=int(x):
            raise ValueError("Input parameter not expressable as a byte, ie not in [0,255]")


class SimulatorActions(Enum):
    """An enum listing the possible actions that can be sent to the robot"""
    moveForwards = 1
    rotate = 2
    kick = 3
    ungrab = 4
    grab = 5
