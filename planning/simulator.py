from enum import Enum

class Simulator(object):

    def __init__(self, debug=False):
        self.currentActionQueue=[]
        self.grabbed=True
        self.holdingBall=False

    # move holonomically at an angle of `degrees` anticlockwise and a distance of `distance` cm
    def holo(self,degrees,distance):
        checkValid(degrees,distance)
        # TODO
        pass

    # move holonomically at an angle of `degrees` clockwise and a distance of `distance` cm
    def holoneg(self,degrees,distance):
        checkValid(degrees,distance)
        pass

    # stop all motors
    def stop(self):
        self.currentActionQueue=[]

    # rotate `degrees` degrees anticlockwise, then move `distance` cm
    def rotate(self,distance,degrees):
        checkValid(degrees,distance)
        if degrees>0:
            self.currentActionQueue.append({'action': SimulatorActions.rotate, 'amount': degrees, 'timeSpent': 0})
        if distance>0:
            self.currentActionQueue.append({'action': SimulatorActions.moveForwards, 'amount': distance, 'timeSpent': 0})

    # rotate `degrees` degrees clockwise, then move `distance` cm
    def rotateneg(self,distance,degrees):
        checkValid(degrees,distance)
        if degrees>0:
            self.currentActionQueue.append({'action': SimulatorActions.rotate, 'amount': -degrees, 'timeSpent': 0})
        if distance>0:
            self.currentActionQueue.append({'action': SimulatorActions.moveForwards, 'amount': distance, 'timeSpent': 0})

    # kick with power `distance`
    def kick(self,distance):
        checkValid(distance)
        self.currentActionQueue.append({'action': SimulatorActions.ungrab, 'timeSpent': 0})
        self.currentActionQueue.append({'action': SimulatorActions.kick, 'amount': distance, 'timeSpent': 0})
        self.currentActionQueue.append({'action': SimulatorActions.grab, 'timeSpent': 0})

    # cancel previous command and any queued commands
    def flush(self):
        self.currentActionQueue=[]

    # grab the ball
    # ensure the grabber is opened before calling!
    def grab(self):
        self.currentActionQueue.append({'action': SimulatorActions.grab, 'timeSpent': 0})

    # open the grabber, ready to grab
    def ungrab(self):
        self.currentActionQueue.append({'action': SimulatorActions.ungrab, 'timeSpent': 0})

    def tick(self):
        '''Update the status of our robot and the ball based on our recent actions'''
        pass


def checkValid(*toCheck):
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

