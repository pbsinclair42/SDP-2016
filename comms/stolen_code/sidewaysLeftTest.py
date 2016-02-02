from RobotCommunications import RobotCommunications
import time


r = RobotCommunications(debug=True)
r.moveSideways(100)
time.sleep(1)
r.stop()

