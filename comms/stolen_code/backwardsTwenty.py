from RobotCommunications import RobotCommunications
import time


r = RobotCommunications(debug=True)
r.moveBackwards(100)
time.sleep(2.3)
r.stop()
