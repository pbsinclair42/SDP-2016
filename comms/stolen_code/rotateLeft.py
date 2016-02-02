from RobotCommunications import RobotCommunications
import time


r = RobotCommunications(debug=True)
r.rotateLeft(100)
time.sleep(2)
r.stop()
