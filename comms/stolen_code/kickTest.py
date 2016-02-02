from RobotCommunications import RobotCommunications
import time

r = RobotCommunications(debug=False)
r.grab(100)
time.sleep(0.5)
r.kick(100)
time.sleep(0.5)
r.stop()
