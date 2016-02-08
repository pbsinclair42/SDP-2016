from tracker import *
from camera import *

c = Camera()
t = RobotTracker('yellow', 1)

f = c.get_frame()

print ('Oponent defender')
print t.opponent_defender_coordinates(f)

print ('Oponent attacker')
print t.opponent_attacker_coordinates(f)

print ('Our defender')
print t.our_defender_coordinates(f)

print ('Our attacker')
print t.our_attacker_coordinates(f)

