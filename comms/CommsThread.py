from serial import Serial
from multiprocessing import Process, Pipe, Event
from time import sleep, time

def comms_thread(pipe_in, pipe_out, event, port, baudrate):

    cmnd_list, data_buffer = [], []
    radio_connected = False
    ack_count = (0, 0)
    prev_ack_count = ack_count
    seq_num = 0
    command_sleep_time = 0.005 # sleep time between sending each byte
    process_sleep_time = 0.05 # sleep time for process
    # robot state parameters
    robot_state = {
        "mag_head" : 0,
        "buffer"   : [0, 0, 0], # Overflow, buffer, command index
        "seq_num"  : 0,
        "grabber"  : 0, # 0: closed, 1: open,
        "active"   : False
    }
    atomic_status = None
    prev_mag_state = robot_state["mag_head"]

    # perform setup
    while not radio_connected:
        
        for item in range(0, 10):
            try:
                port = port[:-1] + str(item)
                comms = Serial(port=port, baudrate=baudrate)
                radio_connected = True
                break
            except Exception as e:
                print "Failed to connect radio with port", str(port), str(e)
                radio_connected = False
                sleep(5)
    print "Radio On-line"
    
    while True:
        event.wait()
        # to account for processing delay in sleep cycles
        start_time = time()

        # get all pipe data
        while pipe_in.poll():
            pipe_data = pipe_in.recv()

            if isinstance(pipe_data, tuple):
                # get a tuple to reduce risk of data damage,
                # then turn to a list to support mutability
                # also add-in flags for: [SENT, ACKNOWLEDGED, FINISHED]
                command = [ord(item) for item in pipe_data[0]] + [0, 0 ,0]
                if cmnd_list and is_holo(command) and is_holo(cmnd_list[-1]):
                    cmnd_list[-1] = command
                else:
                    cmnd_list.append(command)

            # non-command-inputs:
            elif pipe_data == "exit":
                return

            # return index of command currently being performed
            # elif pipe_data == "ccmd":
            #    pipe_out.send(len(cmnd_list) == ack_count[1])

            elif pipe_data == "rprt":
                print cmnd_list
                print data_buffer

            elif pipe_data == "flush":
                cmnd_list = []
                data_buffer = []
                ack_count = (0, 0)
                while comms.in_waiting:
                    print "Flushing", ord(comms.read(1))
            
            elif pipe_data in ["grab", "ungrab"]:
                atomic_status = pipe_data


        # get all data
        while comms.in_waiting:
            data = comms.read(1)
            data_buffer += [ord(data)]

        try:
        # ensure data has been processed before attempting to send data
            data_buffer = process_data(data_buffer, robot_state)
            process_state(cmnd_list, robot_state)
        except IndexError:
            for i in range(0, 1000):
                print "You did not manage to reset the arduino :/"

        if not robot_state["active"]:
            print "comms: arduino not responding yet"
            sleep(1) # sleep and try to connect to arduino again
            continue


        cmd_to_send = fetch_command(cmnd_list)
        
        if cmd_to_send:
            sequenced = sequence_command(cmd_to_send[:4], robot_state["seq_num"])
            for command_byte in sequenced:
                comms.write(sequenced)
                sleep(command_sleep_time)
            print "Sending command: ", sequenced, "SEQ:", robot_state["seq_num"]
        
        #handle atomic operations
        if atomic_status == "grab" and robot_state["grabber"] == False:
            # send atomic command with both possible sequence numbers.
            atomic_command = [ord(item) for item in [16, 255, 255, 255]]
            sequenced = sequence_command(atomic_command, 0)
            for command_byte in sequenced:
                comms.write(sequenced)
                sleep(command_sleep_time)
            print "Sending command: ", sequenced, "SEQ:", 0
            
            sequenced = sequence_command(atomic_command, 1)
            for command_byte in sequenced:
                comms.write(sequenced)
                sleep(command_sleep_time)
            print "Sending command: ", sequenced, "SEQ:", 1
        
        elif atomic_status == "ungrab" and robot_state["grabber"] == True:
            atomic_command = [ord(item) for item in [32, 255, 255, 255]]
            sequenced = sequence_command(atomic_command, 0)
            for command_byte in sequenced:
                comms.write(sequenced)
                sleep(command_sleep_time)
            print "Sending command: ", sequenced, "SEQ:", 0
            
            sequenced = sequence_command(atomic_command, 1)
            for command_byte in sequenced:
                comms.write(sequenced)
                sleep(command_sleep_time)
            print "Sending command: ", sequenced, "SEQ:", 1

        # computer ack count
        ack_count = (sum([command[-2] for command in cmnd_list]), sum([command[-1] for command in cmnd_list]) )
       
        # report back to main process
        if ack_count != prev_ack_count:
            pipe_out.send(ack_count)
            prev_ack_count = ack_count
        if robot_state["mag_head"] != prev_mag_state:
            pipe_out.send(robot_state["mag_head"])
            prev_mag_state = robot_state["mag_head"]
        #print robot_state
        sleep(process_sleep_time)

def process_data(data, robot_state):
    "Reverse all the incoming data, find the *LAST* valid command, and delete the rest"
    for idx, item in enumerate(reversed(data)):
        if item == 253 and idx >  6:
            checksum, locale = 0, 1
            for cmd_idx in range(idx, idx  - 7, -1):
                checksum += sum([bit == '1' for bit in bin(data[len(data) - 1 - cmd_idx])]) * locale
                locale += 1
            checksum = 255 - checksum
            if checksum ==  data[len(data) - 1 - idx + 7]:
                offset = len(data) - 1
                robot_state["buffer"] = [data[offset - idx + 1], data[offset - idx + 2], data[offset - idx + 3]]
                robot_state["mag_head"] = data[offset - idx + 4] + data[offset - idx + 5]
                robot_state["seq_num"] = data[offset - idx + 2] / 4 % 2
                robot_state["grabber"] = data[offset - idx + 6] == 1
                robot_state["active"] = True
                del data
                return []
    return data
def process_state(cmnd_list, robot_state):
    """Set command_list flags, based on robot state, parsed from incoming comms"""
    # if this is the first command and it has not been sent
    if cmnd_list and len(cmnd_list) == 1 and cmnd_list[0][-3:] == [0, 0, 0]:
        if robot_state["buffer"] != [0, 0, 0]:
            command_bias = robot_state["buffer"][0] * 64 + robot_state["buffer"][1] / 4
            for item in range(0, command_bias):
                cmnd_list.insert(0, [255, 255, 255, 255, 1, 1, 1])
            print "Corrected State", cmnd_list, range(0, command_bias)


    # see if everything is received
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

def fetch_command(cmnd_list):
    total_commands = len(cmnd_list)
    if total_commands and not cmnd_list[-1][-2]:
        try:
            #get first un-sent or un-acknowledged command
            cmd_index, cmd_to_send = ((idx, command) for (idx, command) in enumerate(cmnd_list) if command[-3] == 0 or command[-2] == 0).next()
            cmnd_list[cmd_index][-3] = 1
            return cmd_to_send
        except StopIteration:
            # return None if there are no commands to be sent
            return None
    else:
        # return None if there are no commands to find
        return None
def is_holo(command):
    return command[0] >= 124 and command[0] <= 127
if __name__ == "__main__":
    rs = {}
    process_data([253, 0, 0, 0, 154, 0, 228], rs)
    print rs