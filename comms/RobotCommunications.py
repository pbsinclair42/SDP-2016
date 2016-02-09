from Communications import Communications


class RobotCommunications(Communications):

    LEFT_WHEEL_MOTOR = 1
    RIGHT_WHEEL_MOTOR = 2
    BACK_WHEEL_MOTOR = 3
    KICK_MOTOR = 4

    def __init__(self, debug=False):
        super(RobotCommunications, self).__init__(debug)


    def holo(self,degrees,distance):
        x = self.write(chr(2) + chr(degrees) + chr(distance) +chr(255))
        return x
    def holoneg(self,degrees,distance):
        x = self.write(chr(130) + chr(degrees) + chr(distance) +chr(255))
        return x
    def stop(self):
        x=self.write(chr(8)+chr(255)+chr(255)+chr(255))
        return x
    def rotate(self,distance,degrees):
        x = self.write(chr(1) +chr(degrees)+chr(distance) + chr(255))
        return x
    def rotateneg(self,distance,degrees):
        x = self.write(chr(129) +chr(degrees)+chr(distance) + chr(255))
        return x
    def kick(self,distance):
        x = self.write(chr(4)+chr(distance)+chr(255)+chr(255))
        return x
    def flush(self):#stop previous command
        x = self.write(chr(128)+chr(255)+chr(255)+chr(255))
        return x
    def grab(self):#grab
        x = self.write((chr(16) + chr(255)+chr(255)+chr(255)))
        return x
    def ungrab(self):
        x = self.write(chr(32) + chr(255)+chr(255)+chr(255))
        return x
    def flush(self):
        x = self.write(chr(64) + chr(255)+chr(255)+chr(255))
        return x
    def test(self, argument):#test comms
        print 'I got your message: ' + str(argument)

