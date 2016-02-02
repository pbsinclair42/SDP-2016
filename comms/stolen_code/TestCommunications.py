from Communications import Communications

# This class is the same as robot communications but instead of talking to arduino, it just prints commands to console.
class TestCommunications(Communications):

    LEFT_WHEEL_MOTOR = 1
    RIGHT_WHEEL_MOTOR = 2
    BACK_WHEEL_MOTOR = 3
    KICK_MOTOR = 4

    def __init__(self, debug=False):
        pass
        #super(TestCommunications, self).__init__(debug)

    # Stops all motors
    def stop(self):
        print 'STOP'

    # Straight movement
    def moveStraight(self, motorPower):
        print "MOVE STRAIGHT " + str(motorPower)

    def stopStraight(self, motorPower):
        print "STOP_STRAIGHT + " + str(motorPower)

    # Sideways LEFT  = -motorPower
    # Sideways RIGHT = +motorPower
    def moveSideways(self, motorPower):
        print "MOVE SIDEWAYS " + str(motorPower)

    # Same as Sideways, it's just diagonal
    def moveDiagonalLeft(self, motorPower):
        print "MOVE DIAGONAL " + str(motorPower)

    def moveDiagonalRight(self, motorPower):
        print "MOVE DIAGONAL " + str(motorPower)

    # Rotate LEFT  = -motorPower
    # Rotate RIGHT = +motorPower
    def rotate(self, motorPower):
        print "ROTATE " + str(motorPower)

    # Rotate and Grab - 2 args: power_rotate, power_grab
    def rotate_and_grab(self, motorPower_r, motorPower_g):
        self.write("RG " + str(motorPower_r) + " " + str(motorPower_g))

    def stopRotate(self, motorPower):
        print "STOP_ROTATE " + str(motorPower)

    # Grab and Kick take motorPower. The values should be predefined depending
    # on how far we need to kick or grab (it will probably be a constant)
    def grab(self, motorPower):
        print "ACTION GRAB " + str(motorPower)

    def grab_cont(self, motorPower):
        self.write("ACTION GRAB_CONT " + str(motorPower))

    def kick(self, motorPower):
        print "ACTION KICK " + str(motorPower)
