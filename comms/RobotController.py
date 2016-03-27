from CommsThread import comms_thread
from multiprocessing import Process, Pipe, Event
from time import sleep

# the ideal distance from the edge of our robot that we should grab the ball from (centimeters)
GRAB_DISTANCE = 5.0
# the ideal distance from the edge of our robot that we should open our claws to then grab the ball from (centimeters)
UNGRAB_DISTANCE = 30.0


class RobotController(object):
    """
        A thread-based API for the communication system. See the command_dict for command-based firmware API
    """
    def __init__(self,
                 port="/dev/ttyACM0",
                 baudrate=115200,
                 debug=False):
        """
            Initialize firware API and start the communications parallel process
        """
        self.grabbed = True
        self.ack_counts = (0, 0)
        self.mag_heading = 0
        self.commands = 0
        self.command_list = []
        self.command_dict = {
            "ROT_MOVE_POS" : chr(3  ),
            "HOL_MOVE"     : chr(124),
            "KICK"         : chr(4  ),
            "STOP"         : chr(8  ),
            "GRAB"         : chr(16 ),
            "UNGRAB"       : chr(32 ),
            "FLUSH"        : chr(64 ),

            "DONE"         : chr(250),
            "ACK"          : chr(253),
            "RESEND"       : chr(252),
            "FULL"         : chr(254),
            "END"          : chr(255)
        }

        self.parent_pipe_in, self.child_pipe_out = Pipe()
        self.child_pipe_in, self.parent_pipe_out = Pipe()
        self.process_event = Event()
        self.process = Process(name="comms_thread",
                               target=comms_thread,
                               args=(self.child_pipe_out, self.child_pipe_in, self.process_event, port, baudrate))
        self.process.start()
    def move(self, angle_to_face=None, angle_to_move=None, distance_to_target=0 , grab_target=False, rotate_in_place=False):
        """ Overriding move function
            
        angle_to_move: Absolute vision angle towards which to move
        angle_to_face: Absolute vision angle towards which to face (while moving) 
        distance_to_target: Distance to target which we're moving towards
        grab_target: whether we want to grab the target(e.g. the ball)
        rotate_in_place: Whether we want the rotation to be in-place, e.g. not to move
        
        """
        self.synchronize()
        current_heading = self.get_mag_heading()
        mag_to_face = self.absolute_to_magnetic(angle_to_face)
        mag_to_move = self.absolute_to_magnetic(angle_to_move)

        #if abs(angle_to_face - current_heading) > 90:
        #    self.rot_move(angle_to_face, 0)
        print "stats", angle_to_face, angle_to_move, rotate_in_place, current_heading
        if angle_to_face is not None and angle_to_move is not None and not rotate_in_place:
	        if distance_to_target < 5 and abs(angle_to_face - current_heading) < 5:
	            self.stop_robot()
	        else:
                    print "move moved holonomically"
	            self.holo(angle_to_move, angle_to_face)
	    
        elif angle_to_face is not None and rotate_in_place:
	    self.rot_move(mag_to_face)

        if distance_to_target <= UNGRAB_DISTANCE and grab_target and self.grabbed:
            self.ungrab(True)
            self.grabbed = False

        if distance_to_target <= GRAB_DISTANCE and abs(angle_to_face - current_heading) < 10 and not self.grabbed and grab_target:
            self.stop_robot()
            self.grab(True)
            self.grabbed = True

    def queue_command(self, command):
        """
            Convenience function to send-in a command, as a tuple to reduce
            data corruption possibility. Command flags are added on receipt
        """
        self.commands += 1
        self.parent_pipe_in.send((command,))
        self.process_event.set()
        self.synchronize()
        print "Queue-ing:", [ord(item) for item in command]

    def rotate(self, degrees):
        """
            A rotation-only function for angles up-to 255 deg
        """
        degrees1 = absolute_to_magnetic(degrees)
        degrees2 = 0
        if degrees1 > 180:
        	degrees2 = 180
        	degrees1 = 180 - degrees1 
        command = self.command_dict(self.command_dict["ROT_MOVE_POS"] + chr(int(degrees1)) + chr(int(degrees2)) + self.command_dict["END"])
        self.queue_command(command)
    def holo(self, dist_vector, angular_vector):
        dist_vector = self.absolute_to_magnetic(dist_vector)
        angular_vector = self.absolute_to_magnetic(angular_vector)
        
        command_byte = ord(self.command_dict["HOL_MOVE"])
        
        if dist_vector > 180:
            command_byte += 1
            dist_vector = dist_vector - 180
        
        if angular_vector > 180:
            command_byte += 2
            angular_vector = angular_vector - 180

        command = chr(command_byte) + chr(int(dist_vector)) + chr(int(angular_vector)) + self.command_dict["END"]
        self.queue_command(command)
    
    def exit(self):
        """
            Exit comms process
        """
        self.parent_pipe_in.send("exit")
        self.process.join()

    def kick(self, power):
        """
            kick
        """
        command = self.command_dict["KICK"] + chr(power) + self.command_dict["END"] + self.command_dict["END"]
        self.queue_command(command)

    def grab(self, atomic=False):
        """
            grab
        """
        if not atomic:
            command = self.command_dict["GRAB"] + chr(0) + self.command_dict["END"] + self.command_dict["END"]
            self.queue_command(command)
        else:
            #command = self.command_dict["GRAB"] + self.command_dict["END"] + self.command_dict["END"] + self.command_dict["END"]
            command = "grab"
            self.parent_pipe_in.send("grab")
            
        

    def ungrab(self, atomic=False):
        """
            ungrab
        """
        if not atomic:
            command = self.command_dict["UNGRAB"] + chr(0) + self.command_dict["END"] + self.command_dict["END"]
            self.queue_command(command)
        else:
            #command = self.command_dict["UNGRAB"] + self.command_dict["END"] + self.command_dict["END"] + self.command_dict["END"]
            command = "ungrab"
            self.parent_pipe_in.send("ungrab")
        

    def flush(self):
        """
            flush comms and arduino buffers
        """
        self.commands = 0
        self.ack_counts = (0, 0)
        self.queue_command("flush");
        command = self.command_dict["FLUSH"] + self.command_dict["END"] + self.command_dict["END"] + self.command_dict["END"]
        self.queue_command(command)

    def stop_comms(self):
        """
            stop communications process until a new command has been issued
        """
        self.process_event.clear()
    
    def stop_robot(self):
        command = self.command_dict["STOP"] + self.command_dict["END"] + self.command_dict["END"] + self.command_dict["END"]
        self.queue_command(command)

    def report(self):
        """
            Return a report of sent commands and currently-buffered data
        """
        self.parent_pipe_in.send("rprt")
    def synchronize(self):
        while self.parent_pipe_out.poll():
            item = self.parent_pipe_out.recv()
            if isinstance(item, tuple):
                self.ack_counts = item
            else:
                self.mag_heading = item

    def restart(self):
        self.process_event.set()
        self.parent_pipe_in.send("restart");

    def am_i_done(self):
        self.synchronize()
        if self.ack_counts[0] == self.commands and self.ack_counts[1] == self.commands:
            #print self.ack_counts, self.commands
            return True
        else:
            return False
    def get_mag_heading(self):
        self.synchronize()
        return self.mag_heading

    def absolute_to_magnetic(self, angle):
    	mag_north = 157

    	if angle is None:
    		return None
        # scale from 0 to 360
        if angle < 0:
            angle = 360 - abs(angle)

        # reverse
        angle = 360 - angle

        angle = angle + mag_north

        if angle > 360:
            angle = abs(360 - abs(angle))
        return angle

if __name__ == "__main__":
    r = RobotController()
    deg = 0
    while True:
        deg += 30
        deg %= 360
        r.move(angle_to_move=deg, angle_to_face=deg, distance_to_target=None, grab_target=False, rotate_in_place=False)
        sleep(1)
