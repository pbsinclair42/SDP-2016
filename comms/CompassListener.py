from serial import Serial
import time
comms = Serial(port="/dev/ttyACM4", baudrate=115200)
data = []
data = ""
while True:
    start = time.time()
    while comms.in_waiting:
        data +=  str(comms.read(1))
        print data