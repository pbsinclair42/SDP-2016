from RobotCommunications import RobotCommunications
import time

r = RobotCommunications()


def rot_180(n):
    if 360 % n == 0:
        for i in range(0, 360 / n):
            r.rotate(0, n)
            time.sleep(2)
    else:
        print("error")

while True:
    n = int(input(">>"))
    rot_180(n)
