from serial import Serial
from multiprocessing import Process, Pipe, Event
from time import sleep

class CommsThread(object):
    
    def __init__(self,
    	         port="/dev/ttyACM0",
    	         baudrate=115200):
    self.command_list = []
    self.command_dict = {
    	"CMD_DONE" : chr(1),
    	#add the rest
    }
    self.parent_pipe_end, self.child_pipe_end = Pipe()
    self.process_event = multiprocessing.Event()
    self.process = Process(name="comms_thread",
                           target=self.comms_thread,
                           args=(self.child_pipe_end, self.process_event))
    self.process.start()

    def queue_command(self, command):
    	self.parent_pipe_end.send(command)
    	self.command_list.append((command, 0, 0))
    	self.process_event.set()

def comms_thread(self, pipe, event):
	cmnd_list = []
	while True:
		event.wait()
		if pipe.poll():
			pipe_data = pipe.recv()
			if isinstance(pipe_data, tuple):
				cmnd_list.append(pipe_data)
				pass
				#send_command
			if cmnd_list[-1][2] != 1:
				pass
				#listen for output


