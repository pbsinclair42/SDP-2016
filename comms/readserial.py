import serial
#Modified code from main loop:
s = serial.Serial(5)

#Modified code from thread reading the serial port
while 1:
  tdata = s.read()           # Wait forever for anything
  time.sleep(1)              # Sleep (or inWaiting() doesn't give the correct value)
  data_left = s.inWaiting()  # Get the number of characters ready to be read
  tdata += s.read(data_left) # Do the read and combine it with the first character

  ... #Rest of the code
