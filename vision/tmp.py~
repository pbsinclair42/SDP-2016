from camera import Camera
from calibrate import *
import cv2

cal = Calibrate()
def do_thing():
  c = Camera()

  while True:
    frame = cal.step(c.get_frame())
    cal.show_frame(frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  cv2.destroyAllWindows()
