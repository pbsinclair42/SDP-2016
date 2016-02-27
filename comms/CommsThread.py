from serial import Serial
from multiprocessing import Process, Pipe, Event
from time import sleep

class CommsThread(object):
    
    def __init__(self,
                 port="/dev/ttyACM0",
                 baudrate=115200):
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

	    self.parent_pipe_end, self.child_pipe_end = Pipe()
	    self.process_event = multiprocessing.Event()
	    self.process = Process(name="comms_thread",
	                           target=comms_thread,
	                           args=(self.child_pipe_end, self.process_event, port, baudrate))
	    self.process.start()

    def queue_command(self, command):
        self.parent_pipe_end.send(command)
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


def comms_thread(self, pipe, event, port, baudrate):
    cmnd_list = []
    data_buffer = []
    radio_connected = False

    while not radio_connected:
	    try:
	        comms = serial.Serial(port=port, baudrate=baudrate)
	    	radio_connected = True
	    except:
	        print "Comms: Radio not connected. Trying again in 5 seconds"
	        radio_connected = False
	        sleep(5)	

    while True:
        event.wait()
        if pipe.poll():
            pipe_data = pipe.recv()
            
            #if you've received a command - send it
            if isinstance(pipe_data, tuple):
                cmnd_list.append(pipe_data)
                comms.write(pipe_data[0])
            
            # non-command-inputs:
            elif pipe_data == "exit":
            	return
        while comms.inWaiting():
        	data_buffer_buffer.append(comms.read(1))

        process_data(cmnd_list, data_buffer)
        sleep(0.5)

def process_data(commands, data):
	print "Commands:", 
	for item in commands:
		print item, 
	print "Data:"
	for item in data:
		print item, 


