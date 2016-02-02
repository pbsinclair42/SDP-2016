import time
import serial
import os
# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
    port='/dev/ttyACM0',
    baudrate=115200
    #parity=serial.PARITY_ODD,
    #stopbits=serial.STOPBITS_TWO,
    #bytesize=serial.SEVENBITS
)

ser.isOpen()

ser.write(bytes('c'))

with open("test_group_4.bin", "rb") as f:
    while True:
        chunk = f.read(1)
	if chunk:
	    ser.write(chunk)
	    time.sleep(0.03)
	else:
	    break

ser.close()
