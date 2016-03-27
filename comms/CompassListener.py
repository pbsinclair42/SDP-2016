from serial import Serial
import time
comms = Serial(port="/dev/ttyACM3", baudrate=115200)
data = []
data = ""
print "start"
while True:
    while comms.in_waiting:
        print comms.read(1)