from serial import Serial
from multiprocessing import Process, Pipe, Event
from time import sleep
from struct import unpack

class CommsThread(object):
    
    def __init__(self,
                 port="/dev/ttyACM0",
                 baudrate=115200,
                 debug=False):
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
        self.parent_pipe_in.send((command, 0, 0))
        #self.command_list.append((command, 0, 0))
        self.process_event.set()
    
    def move(self, distance):
        command = self.command_dict["ROT_MOVE_POS"] + chr(0) + chr(distance) + self.command_dict["END"]
        self.queue_command(command)
    
    def rotate(self, degrees):
        if degrees >= 0:
            command = self.command_dict["ROT_MOVE_POS"] + chr(degrees) + chr(0) + self.command_dict["END"]
        else:
            command = self.command_dict["ROT_MOVE_NEG"] + chr(degrees) + chr(0) + self.command_dict["END"]
        self.queue_command(command)
    def rot_move(self, distance, degrees):
        if degrees >= 0:
            command = self.command_dict["ROT_MOVE_POS"] + chr(degrees) + chr(distance) + self.command_dict["END"]
        else:
            command = self.command_dict["ROT_MOVE_NEG"] + chr(degrees) + chr(distance) + self.command_dict["END"]
        self.queue_command(command)

    def holo(self, dist_vector, angular):
        pass

    def exit(self):
        self.process.join()

    def current_cmd(self):
        self.parent_pipe_in.send("ccmd")
        while not self.parent_pipe_out.poll():
            pass
        return self.parent_pipe_out.recv()

    def report(self):
           self.parent_pipe_in.send("rprt")


def comms_thread(pipe_in, pipe_out, event, port, baudrate):
    cmnd_list = []
    data_buffer = []
    radio_connected = False

    while not radio_connected:
        try:
            comms = Serial(port=port, baudrate=baudrate)
            radio_connected = True
        except Exception as e:
            print "Comms: Radio not connected. Trying again in 5 seconds;", str(e)
            radio_connected = False
            sleep(5)    
    print "Radio On-line"
    
    while True:
        event.wait()
        if pipe_in.poll():
            pipe_data = pipe_in.recv()
            
            #if you've received a command - send it
            if isinstance(pipe_data, tuple):
                # get a tuple to reduce risk of data damage,
                # then turn to a list to support mutability
                cmnd_list.append([ord(item) for item in pipe_data[0]] + [0 ,0])
                comms.write(pipe_data[0])
                print "Sending: ", pipe_data[0]
            
            # non-command-inputs:
            elif pipe_data == "exit":
                return

            elif pipe_data == "ccmd":
                target = 0
                for idx, item in enumerate(cmnd_list):
                    if item[2] == 0:
                        target = idx;
                        break;
                pipe_out.send(target)

            elif pipe_data == "rprt":
                print "Commands:"
                for item in cmnd_list:
                    print item,
                print "Data:"
                print data_buffer

        while comms.in_waiting:
            data = comms.read(1)
            try:
            	data_buffer.append(ord(data))
            	#data_buffer.append((data, ord(data), str(data), int(data), int(str(data)), unpack('B', data)[0]))
            except ValueError:
            	pass
        process_data(cmnd_list, data_buffer)
        sleep(0.25)

def process_data(commands, data):
    pass
    # for idx, item in enumerate(data):
    # print idx, item

if __name__ == "__main__":
	c = CommsThread()
	c.rotate(200)

	sleep(3)
	c.report()