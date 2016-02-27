import serial
import time


class Communications(object):

    def __init__(self,
                 debug=False,
                 setConnectionOff=False,
                 port='/dev/ttyACM0',
                 baudrate=9600,
                 #timeout=2
                 ):
        self.current_cmd = 0;
        if setConnectionOff is False:

            try:
                self.port = serial.Serial(port=port, baudrate=baudrate)
                self.debug = debug
                time.sleep(0.5)
            except:
                raise BaseException("Radio not connected or wrong port supplied.")

    def write(self, command):
        self.port.write(command + '')
        #time.sleep(0.005)
        out = ''
        while self.port.inWaiting() >0:
            out += self.port.read(1)
        if ord(out[-1]) == 111:
            self.current_cmd += 1
            print("CMD_DONE")
        elif out =="CMD_RESEND":#resend
            print("RESEND")
            write(command)
        elif out =="CMD_FULL":#full
            print("FULL")
            time.sleep(0.005)
            write(command)
        elif out == "CMD_ERROR":#error
            print("ERROR")
            write(command)
        elif out != '':
            print ">>" + out
            return out
            #might want to return this so the planner can use it
        if self.debug:
            print self.port.readline()
