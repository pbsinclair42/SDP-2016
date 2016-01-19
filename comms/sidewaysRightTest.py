from RobotCommunications import RobotCommunications
import time


r = RobotCommunications(debug=True)
r.moveSidewaysRight(100)
time.sleep(1)
r.stop()

