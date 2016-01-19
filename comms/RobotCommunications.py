from Communications import Communications


class RobotCommunications(Communications):

    LEFT_WHEEL_MOTOR = 1
    RIGHT_WHEEL_MOTOR = 2
    BACK_WHEEL_MOTOR = 3
    KICK_MOTOR = 4

    def __init__(self, debug=False):
        super(RobotCommunications, self).__init__(debug)

    # Stops all motors
    def stop(self):
        self.write("s")

    # Straight movement
    def moveStraight(self, motorPower):
        self.write("f");# + str(motorPower))

    def moveBackwards(self, motorPower):
        self.write("b")# + str(motorPower);

    #move left
    def moveLeft(self,motorPower):
        self.write("l")# + str(motorPower))

    #move right
    def moveRight(self,motorPower):
        self.write("r")#+str(motorPower))

    # Same as Sideways, it's just diagonal
    def moveDiagonalLeft(self, motorPower):
        self.write("d")# + str(motorPower))

    def moveDiagonalRight(self, motorPower):
        self.write("e")# + str(motorPower))

    def rotateLeft(self, motorPower):
        self.write("o")# + str(motorPower))

    def rotateRight(self, motorPower):
        self.write("p")# + str(motorPower))

    """
    # Rotate and Grab - 2 args: power_rotate, power_grab
    def rotateAndGrab(self, motorPower_r, motorPower_g):
        self.write("ROTATE_GRAB " + str(motorPower_r) + " " + str(motorPower_g))

    def stopRotate(self, motorPower):
        self.write("STOP_ROTATE " + str(motorPower))

    # Grab and Kick take motorPower. The values should be predefined depending
    # on how far we need to kick or grab (it will probably be a constant)
    def grab(self, motorPower):
        self.write("ACTION GRAB " + str(motorPower))

    def grab_cont(self, motorPower):
        self.write("ACTION GRAB_CONT " + str(motorPower))

    def kick(self, motorPower):
        self.write("ACTION KICK " + str(motorPower))

    def test(self, argument):
        print 'I got your message: ' + str(argument)
    """
