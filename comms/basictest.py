import time
import serial

# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
        port='/dev/ttyACM0',
        baudrate=9600,
        #parity=serial.PARITY_ODD,
        #stopbits=serial.STOPBITS_TWO,
        #bytesize=serial.SEVENBITS
        )

ser.isOpen()


ser.write('f')
time.sleep(1)
ser.write('s')
time.sleep(1)
ser.write('f')
time.sleep(1)
ser.write('s')
time.sleep(1)
ser.write('l')
time.sleep(1)
ser.write('s')
time.sleep(1)
ser.write('l')
time.sleep(1)
ser.write('s')
time.sleep(1)
ser.write('b')
time.sleep(1)
ser.write('s')
time.sleep(1)
ser.write('b')
time.sleep(1)
ser.write('s')
time.sleep(1)
ser.write('r')
time.sleep(1)
ser.write('s')
time.sleep(1)
ser.write('r')
ser.write('s')
time.sleep(1)



