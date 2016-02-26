from RobotCommunications import RobotCommunications
import time

r = RobotCommunications()


def rot_180(a, d):
    if 360 % a == 0:
        for i in range(0, 360 / a):
            r.rotate(d, a)
            time.sleep(2)
    else:
        print("error")

while True:
    a = int(input("angle:"))
    d = int(input("distence:"))
    rot_180(a, d)
