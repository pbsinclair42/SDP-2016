class Simulator(object):

    def __init__(self, debug=False):
        self.currentActionQueue=[]
        self.grabbed=True
        self.holdingBall=False

    # move holonomically at an angle of `degrees` anticlockwise and a distance of `distance` cm
    def holo(self,degrees,distance):
        # TODO
        pass

    # move holonomically at an angle of `degrees` clockwise and a distance of `distance` cm
    def holoneg(self,degrees,distance):
        pass

    # stop all motors
    def stop(self):
        self.currentActionQueue=[]

    # rotate `degrees` degrees anticlockwise, then move `distance` cm
    def rotate(self,distance,degrees):
        pass

    # rotate `degrees` degrees clockwise, then move `distance` cm
    def rotateneg(self,distance,degrees):
        pass

    # kick with power `distance`
    def kick(self,distance):
        pass

    # cancel previous command and any queued commands
    def flush(self):
        self.currentActionQueue=[]

    # grab the ball
    # ensure the grabber is opened before calling!
    def grab(self):
        pass

    # open the grabber, ready to grab
    def ungrab(self):
        pass

    def tick(self):
        pass
