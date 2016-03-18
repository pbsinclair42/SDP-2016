from serial import Serial
from multiprocessing import Process, Pipe, Event
from time import sleep, time
from struct import unpack

class CommsThread(object):
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
        self.ack_counts = (0, 0)
        self.mag_heading = 0
        self.commands = 0
        self.command_list = []
        self.command_dict = {
            "ROT_MOVE_POS" : chr(3  ),
            "ROT_MOVE_NEG" : chr(15),
            "HOL_MOVE_POS" : chr(2  ),
            "HOL_MOVE_NEG" : chr(66),
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

    def queue_command(self, command):
        """
            Convenience function to send-in a command, as a tuple to reduce
            data corruption possibility. Command flags are added on receipt
        """
        self.commands += 1
        self.parent_pipe_in.send((command,))
        self.process_event.set()
        print "Queue-ing:", [ord(item) for item in command]

    def move(self, distance, degrees=0):
        """
            A movement-only function for distance up-to 255 cm
        """
        assert distance <= 255, "Distance should not be longer than 255"
        if degrees:
            self.rot_move(distance, degrees)

        else:
            # add extra commands
            while distance > 255:
                self.queue_command(self.command_dict["ROT_MOVE_POS"] + chr(0) + chr(255) + self.command_dict["END"])
                distance -= 255

            command = self.command_dict["ROT_MOVE_POS"] + chr(int(degrees)) + chr(distance) + self.command_dict["END"]
            self.queue_command(command)

    def rotate(self, degrees, distance=0):
        """
            A rotation-only function for angles up-to 255 deg
        """
        assert degrees <= 255 and degrees >= -255, "Degrees should be in range of [-255, 255]"

        if distance:
            self.rot_move(distance, degrees)

        else:
            if degrees >= 0:
                command = self.command_dict["ROT_MOVE_POS"] + chr(int(degrees)) + chr(0) + self.command_dict["END"]

            else:
                command = self.command_dict["ROT_MOVE_NEG"] + chr((-1 * degrees)) + chr(0) + self.command_dict["END"]

            self.queue_command(command)

    def rot_move(self, degrees, distance):
        """
            Perform movement and/or rotation for any degrees and any distance.
            Assumes both are passed as integers
        """

        offset = 0

        # add positive offset
        while degrees > 255:
            self.rotate(255)
            degrees -= 255

        # add negative offset
        while degrees < -255:
            self.rotate(-255)
            degrees += 255

        # calculate movement offset
        while distance > 255:
            offset += 255
            distance -= 255

        # issue command
        if degrees >= 0:
            command = self.command_dict["ROT_MOVE_POS"] + chr(int(degrees)) + chr(int(distance)) + self.command_dict["END"]
        else:
            command = self.command_dict["ROT_MOVE_NEG"] + chr(int(-1 * degrees)) + chr(int(distance)) + self.command_dict["END"]
        self.queue_command(command)

        # issue movement offset command
        while offset > 0:
            self.move(255);
            offset -= 255

    def holo(self, dist_vector, angular):
        if angular > 180:
            command = self.command_dict["HOL_MOVE_NEG"] + chr(int(angular - 180)) + chr(int(dist_vector)) + self.command_dict["END"]
        else:
            command = self.command_dict["HOL_MOVE_POS"] + chr(int(angular)) + chr(int(dist_vector)) + self.command_dict["END"]
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

    def grab(self):
        """
            grab
        """
        command = self.command_dict["GRAB"] + self.command_dict["END"] + self.command_dict["END"] + self.command_dict["END"]
        self.queue_command(command)

    def ungrab(self):
        """
            ungrab
        """
        command = self.command_dict["UNGRAB"] + self.command_dict["END"] + self.command_dict["END"] + self.command_dict["END"]
        self.queue_command(command)

    def flush(self):
        """
            flush comms and arduino buffers
        """
        self.commands = 0
        self.ack_counts = (0, 0)
        self.queue_command("flush");
        command = self.command_dict["FLUSH"] + self.command_dict["END"] + self.command_dict["END"] + self.command_dict["END"]
        self.queue_command(command)

    def stop(self):
        """
            stop communications process until a new command has been issued
        """
        print 15 * "STOP WAS CALLED"
        self.process_event.clear()
    
    def stop_robot(self):
        command = self.command_dict["STOP"] + self.command_dict["END"] + self.command_dict["END"] + self.command_dict["END"]
        self.queue_command(command)

    def report(self):
        """
            Return a report of sent commands and currently-buffered data
        """
        self.parent_pipe_in.send("rprt")
    def get_all_pipe_data(self):
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
        self.get_all_pipe_data()
        if self.ack_counts[0] == self.commands and self.ack_counts[1] == self.commands:
            #print self.ack_counts, self.commands
            return True
        else:
            return False
    def get_mag_heading(self):
        self.get_all_pipe_data()
        return self.mag_heading


def comms_thread(pipe_in, pipe_out, event, port, baudrate):

    cmnd_list = []
    data_buffer = []
    radio_connected = False
    ack_count = (0, 0)
    seq_num = 0
    command_sleep_time = 0.005 # sleep time between sending each byte
    process_sleep_time = 0.13 # sleep time for process
    # robot state parameters
    robot_state = {
        "mag_head" : 0,
        "buffer"   : [0, 0, 0], # Overflow, buffer, command index
        "seq_num"  : 0
    }

    # perform setup
    while not radio_connected:
        try:
            comms = Serial(port=port, baudrate=baudrate)
            radio_connected = True
        except Exception as e:
            print "Comms: Radio not connected. Trying again in 5 seconds;", str(e)
            radio_connected = False
            sleep(5)
    print "Radio On-line"
    sleep(1)
    # flush commands prior to starting
    
    while True:
        event.wait()
        if pipe_in.poll():
            pipe_data = pipe_in.recv()

            if isinstance(pipe_data, tuple):
                # get a tuple to reduce risk of data damage,
                # then turn to a list to support mutability
                # also add-in flags for: [SENT, ACKNOWLEDGED, FINISHED]
                cmnd_list.append([ord(item) for item in pipe_data[0]] + [0, 0 ,0])

            # non-command-inputs:
            elif pipe_data == "exit":
                return

            # return index of command currently being performed
            elif pipe_data == "ccmd":
                pipe_out.send(len(cmnd_list) == ack_count[1])

            elif pipe_data == "rprt":
                print cmnd_list
                print data_buffer

            elif pipe_data == "flush":
                cmnd_list = []
                data_buffer = []
                ack_count = (0, 0)
                while comms.in_waiting:
                    print "Flushing", ord(comms.read(1))


        while comms.in_waiting:
            data = comms.read(1)
            data_buffer += [ord(data)]

        try:
        # ensure data has been processed before attempting to send data
            #print data_buffer
            process_data(cmnd_list, data_buffer, robot_state)
            data_buffer = []
            process_state(cmnd_list, robot_state)
        except IndexError:
            for i in range(0, 1000):
                print "You did not manage to reset the arduino :/"


        try:
            if cmnd_list and robot_state["buffer"][1] / 4 != len(cmnd_list):
                # get first un-sent command or un-acknowledged, but send
                cmd_index, cmd_to_send = ((idx, command) for (idx, command) in enumerate(cmnd_list) if command[-3] == 0 or command[-2] == 0).next()

                # if the command is not received
                if cmd_to_send[-2] == 0:
                    sequenced = sequence_command(cmd_to_send[:4], robot_state["seq_num"])
                    for command_byte in sequenced:
                        comms.write(sequenced)
                        sleep(command_sleep_time)
                    cmnd_list[cmd_index][-3] = 1
                    print "Sending command: ", cmd_index, sequenced, "SEQ:", robot_state["seq_num"]
        except StopIteration:
            pass

        ack_count = (sum([command[-2] for command in cmnd_list]), sum([command[-1] for command in cmnd_list]) )
        pipe_out.send(ack_count)
        pipe_out.send(robot_state["mag_head"])
        #print robot_state
        sleep(process_sleep_time)

def process_data(commands, data, robot_state):
    "Reverse all the incoming data, find the *LAST* valid command, and delete the rest"
    data.reverse()
    for idx, item in enumerate(data):
        if item == 253 and idx >  5:
            checksum = 0
            for cmd_byte in data[idx - 5: idx + 1]:
                checksum += sum([bit == '1' for bit in bin(cmd_byte)])
            checksum = 255 - checksum
            if checksum ==  data[idx - 6]:
                robot_state["buffer"] = [data[idx - 1], data[idx - 2], data[idx - 3]]
                robot_state["mag_head"] = data[idx - 4] + data[idx - 5]
                robot_state["seq_num"] = data[idx - 2] / 4 % 2
                break;
    del data
def process_state(cmnd_list, robot_state):
    """Set command_list flags, based on robot state, parsed from incoming comms"""
    # if this is the first command and it has not been sent
    if cmnd_list and len(cmnd_list) == 1 and cmnd_list[0][-3:] == [0, 0, 0]:
        if robot_state["buffer"] != [0, 0, 0]:
            command_bias = robot_state["buffer"][0] * 64 + robot_state["buffer"][1] / 4
            for item in range(0, command_bias):
                cmnd_list.insert(0, [255, 255, 255, 255, 1, 1, 1])
            print "Corrected State", cmnd_list, range(0, command_bias)


    # see if everythin is received
    if cmnd_list:
        for idx in range(0, robot_state["buffer"][0] * 64 + robot_state["buffer"][1] / 4):
            cmnd_list[idx][-2] = 1

        if robot_state["buffer"][1] == robot_state["buffer"][2]:
            for idx in range(0, robot_state["buffer"][0] * 64 + robot_state["buffer"][1] / 4):
                cmnd_list[idx][-1] = 1


def sequence_command(command, seq):
    sequence = ord(chr(seq * 128 + command[0]))
    checksum = 0
    for cmd_byte in [sequence, command[1], command[2]]:
        checksum += sum([bit == '1' for bit in bin(cmd_byte)])
    return [sequence] + command[1:3] + [ord(chr(255 - checksum))]

if __name__ == "__main__":
    c = CommsThread()

    c.kick(255)
