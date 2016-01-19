import serial
import time


class Communications(object):

    def __init__(self,
                 debug=False,
                 setConnectionOff=False,
                 port='/dev/ttyACM0',
                 baudrate=9600,
                 timeout=2):
        if setConnectionOff is False:

            try:
                self.port = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
                self.debug = debug
                time.sleep(0.5)
            except:
                raise BaseException("Radio not connected or wrong port supplied.")

    def write(self, command):
        self.port.write(command + '\r\n')
        if self.debug:
            print self.port.readline()
