import cv2 
from calibrate import *
from tools import *

frame = cv2.imread('Pitch1.png')
img  = step(frame, 1)


while(1):

    cv2.imshow("IMG", img)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break
#cv2.imwrite("perspective.png", img)
data = get_dimensions(0)
print data
for key in data:
    print key
    print data[key]

cv2.destroyAllWindows()
