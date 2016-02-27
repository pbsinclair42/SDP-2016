import time
from RobotCommunications import RobotCommunications
r = RobotCommunications()

r.rotateneg(90,90)
r.rotate(200, 90)
r.rotate(90, 90)
r.rotate(200, 90)
#r.grab()
#r.ungrab()
#r.rotate(0,10)
"""sleep(4)
r.rotate(0,180)
sleep(4)
r.kick(50)
sleep(1)
grab()
sleep(2)
holo(0,150)
sleep(3)
flush()
kick(100)
sleep(2)"""
