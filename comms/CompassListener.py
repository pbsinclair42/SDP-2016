from serial import Serial
import time
comms = Serial(port="/dev/ttyACM0", baudrate=115200)
data = []
data = ""
while True:
    while comms.in_waiting:
        print comms.read(1)