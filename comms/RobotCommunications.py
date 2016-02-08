from Communications import Communications


class RobotCommunications(Communications):

    LEFT_WHEEL_MOTOR = 1
    RIGHT_WHEEL_MOTOR = 2
    BACK_WHEEL_MOTOR = 3
    KICK_MOTOR = 4

    def __init__(self, debug=False):
        super(RobotCommunications, self).__init__(debug)


    def holo(self,degrees,distance):
        self.write(chr(2) + chr(degrees) + chr(distance) +chr(255))
    def holo2(self,degrees,distance):
        self.write(chr(130) + chr(degrees) + chr(distance) +chr(255))
    def stop(self):# Stops all motors
        self.write(chr(8)+chr(255)+chr(255)+chr(255))
    def rotate(self,distance,degrees):
        self.write(chr(1) +chr(degrees)+chr(distance) + chr(255))
    def rotate2(self,distance,degrees):
        self.write(chr(129) +chr(degrees)+chr(distance) + chr(255))
    def kick(self,distance):
        self.write(chr(4)+chr(distance)+chr(255)+chr(255))
    def flush(self):#stop previous command
        self.write(chr(255)+chr(255)+chr(255)+chr(255))
    def grab(self):#grab
        self.write((chr(16) + chr(255)+chr(255)+chr(255)))
    def ungrab(self):
        self.write(chr(32) + chr(255)+chr(255)+chr(255))
    def flush(self):
        self.write(chr(64) + chr(255)+chr(255)+chr(255))
    def test(self, argument):#test comms
        print 'I got your message: ' + str(argument)

