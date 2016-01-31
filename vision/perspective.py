import numpy as np
import cv2
import argparse

img = cv2.imread('pitch0.jpg')

rows,cols,ch = img.shape

# top-left corner and bottom-right corner (640x480)
#image = cv2.rectangle(img,(610,470),(611,471),(0,255,0),2)

#cv2.imshow('rectangle', image)
pts1 = np.float32([[0,0],[25,476],[609,474],[627,5]])
pts2 = np.float32([[0,0],[0,480],[640,480],[640,0]])

#pts1 = np.float32([[56,65],[368,52],[28,387],[389,390]])
#pts2 = np.float32([[0,0],[300,0],[0,300],[300,300]])

M = cv2.getPerspectiveTransform(pts1,pts2)

dst = cv2.warpPerspective(img,M,(640,480))

cv2.imshow('perspective', dst)
cv2.imwrite('good.jpg', dst)
cv2.waitKey(0)
cv2.destroyAllWindows()

