from tracker import *
from camera import Camera

c = Camera()

frame = c.get_frame()

t = BallTracker('blue')
print t.get_ball_coordinates(frame)