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
        self.command_list = []
        self.command_dict = {
            "ROT_MOVE_POS" : chr(1  ),
            "ROT_MOVE_NEG" : chr(129),
            "HOL_MOVE_POS" : chr(2  ),
            "HOL_MOVE_NEG" : chr(130),
            "KICK"         : chr(4  ),
            "STOP"         : chr(8  ),
            "GRAB"         : chr(16 ),
            "UNGRAB"       : chr(32 ),
            "FLUSH"        : chr(64 ),
            "DONE"         : chr(111),
            "ACK"          : chr(248),
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
        self.parent_pipe_in.send((command,))
        self.process_event.set()
        print "Queue-ing:", [ord(item) for item in command]
    
    def move(self, distance, degrees=0):
        """
            A movement-only function for distance up-to 255 cm
        """
        assert distance >= 255, "Distance should not be longer than 255"
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
        """
           Not yet implemented due to command-length issue
        """
        pass

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
        self.queue_command("flush");
        command = self.command_dict["FLUSH"] + self.command_dict["END"] + self.command_dict["END"] + self.command_dict["END"]
        self.queue_command(command)

    def stop(self):
        """
            stop communications process until a new command has been issued
        """
        self.process_event.clear()

    def current_cmd(self):
        """
            get current command 
        """
        self.parent_pipe_in.send("ccmd")
        while not self.parent_pipe_out.poll():
            pass
        return self.parent_pipe_out.recv()

    def report(self):
        """
            Return a report of sent commands and currently-buffered data
        """
        self.parent_pipe_in.send("rprt")


def comms_thread(pipe_in, pipe_out, event, port, baudrate):
    

    cmnd_list = []
    data_buffer = []
    radio_connected = False
    ack_count = (0, 0)
    
    
    while not radio_connected:
        try:
            comms = Serial(port=port, baudrate=baudrate)
            radio_connected = True
        except Exception as e:
            print "Comms: Radio not connected. Trying again in 5 seconds;", str(e)
            radio_connected = False
            sleep(5)    
    print "Radio On-line"
    
    # flush commands prior to starting
    while comms.in_waiting:
        print "Flushing", ord(comms.read(1))

    resend_time = time()
    


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
                pipe_out.send(ack_count[1])

            elif pipe_data == "rprt":
                print len(cmnd_list), "=?", ack_count
                print "Commands:"
                for item in cmnd_list:
                    print item,
                print "Data:"
                print data_buffer
            
            elif pipe_data == "flush":
                cmnd_list = []
                data_buffer = []
                ack_count = (0, 0)
                while comms.in_waiting:
                    print "Flushing", ord(comms.read(1))


        # if there are commands to send
        if not all(cmnd_list[-1][-3:-1]):
            # get first un-sent command or un-acknowledged, but send
            cmd_index, cmd_to_send = ((idx, command) for (idx, command) in enumerate(cmnd_list) if command[-3] == 0 or command[-2] == 0).next()
            
            # if the command is not acknowledged on time
            if cmd_to_send[-2] == 0 or time() - resend_time > 1.5:
                comms.write(cmd_to_send[:4])
                cmnd_list[cmd_index][-3] = 1
                resend_time = time()
                print "Sending command: ", cmd_index, cmnd_list[cmd_index]
        
        # parse all incoming comms
        while comms.in_waiting:
            data = comms.read(1)
            try:
                data_buffer.append(ord(data))
            except ValueError:
                pass
        ack_count = process_data(cmnd_list, data_buffer, ack_count)
        sleep(0.5)

def process_data(commands, data, comb_count):
    cutoff_index, ack_count, end_count = 0, 0, 0
    for idx, item in enumerate(data):
        if item == 248:
            acknowledge_command(commands, 2)
            cutoff_index = idx
            ack_count += 1
        elif item == 111:
            acknowledge_command(commands, 1)
            cutoff_index = idx
            end_count += 1
    del data[:cutoff_index + 1]
    return (comb_count[0] + ack_count, comb_count[1] + end_count)
    

def acknowledge_command(commands, flag):
    assert flag == 1 or flag == 2
    for item in commands:
        if item[-flag] == 0:
            item[-flag] = 1
            return

if __name__ == "__main__":
    c = CommsThread()

    
    c.rot_move(400, 400)
    #c.move(100)
    sleep(10)
    c.report()
    sleep(2)
    c.exit()