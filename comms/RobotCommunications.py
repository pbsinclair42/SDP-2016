from Communications import Communications


class RobotCommunications(Communications):

    LEFT_WHEEL_MOTOR = 1
    RIGHT_WHEEL_MOTOR = 2
    BACK_WHEEL_MOTOR = 3
    KICK_MOTOR = 4

    def __init__(self, debug=False):
        super(RobotCommunications, self).__init__(debug)

    # TODO: program arduino for holonomic movement
    def holo(self,degrees,distance):
        x = self.write(chr(2) + chr(degrees) + chr(distance) +chr(255))
        return x
    # TODO: program arduino for holonomic movement
    def holoneg(self,degrees,distance):
        x = self.write(chr(130) + chr(degrees) + chr(distance) +chr(255))
        return x
    # TODO: program arduino for stop
    def stop(self):
        x=self.write(chr(8)+chr(255)+chr(255)+chr(255))
        return x
    # rotate `degrees` degrees anticlockwise, then move `distance` cm
    def rotate(self,distance,degrees):
        print("rotate")
        x = self.write(chr(1) +chr(int(degrees))+chr(int(distance)) + chr(255))
        return x
    # rotate `degrees` degrees clockwise, then move `distance` cm
    def rotateneg(self,distance,degrees):
        print("rotateneg")
        x = self.write(chr(129) +chr(int(degrees))+chr(int(distance)) + chr(255))
        #import time
        #time.sleep(degrees/180)
        #self.stop()
        #x = self.write(chr(1) +chr(180-int(degrees))+chr(int(distance)) + chr(255))
        #x = self.write(chr(129) +chr(int(degrees))+chr(int(distance)) + chr(255))
        return x
    # kick with power `distance`
    # TODO: calibrate to match distance
    def kick(self,distance):
        x = self.write(chr(4)+chr(distance)+chr(255)+chr(255))
        return x
    # cancel previous command and any queued commands
    def flush(self):
        x = self.write(chr(128)+chr(255)+chr(255)+chr(255))
        return x
    # grab the ball
    # ensure the grabber is opened before calling!
    def grab(self):
        x = self.write((chr(16) + chr(255)+chr(255)+chr(255)))
        return x
    # open the grabber, ready to grab
    def ungrab(self):
        x = self.write(chr(32) + chr(255)+chr(255)+chr(255))
        return x
    # send a test message to ensure comms are working
    def test(self, argument):
        print 'I got your message: ' + str(argument)

