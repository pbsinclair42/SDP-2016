from serial import Serial
from  time import sleep
comms = Serial(port="/dev/ttyACM0", baudrate=115200)
data = []
while True:
    data = []
    while comms.in_waiting:
        x = ord(comms.read(1))
        data.append(x)
        if x != 253:
        	print x,
        else:
        	print x
    print 80 * "-"
    sleep(1)
    print 80 * "="
    cutoff_index = 0
    data.reverse()
    for idx, item in enumerate(data):
        if item == 253 and idx >  5:
            checksum = 0
            for cmd_byte in data[idx - 5: idx + 1]:
                checksum += sum([bit == '1' for bit in bin(cmd_byte)])
            checksum = 255 - checksum
            print checksum, data[idx - 6]
            print "OVERFLOW", data[idx - 1]
            print "BUF_IND", data[idx - 2]
            print "COM_IND", data[idx - 3]
            print "HEAD", data[idx - 4] + data[idx - 5]
            break