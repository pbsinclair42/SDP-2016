from tracker import *
from camera import Camera
import numpy as np
from numpy.linalg import inv


def meanPoint(points):

    tx = 0.0
    ty = 0.0

    for point in points:
        tx += point[0]
        ty += point[1]

    l = len(points)
    if l == 0:
        return None

    return ( tx / l, ty / l )

def equivalent ( p1, p2 ):
    return p1[0] == p2[0] and p1[1] == p2[1]

def linear_regression( points ):
    
    
    if Tracker.distance(points[0], meanPoint(points)) < 10 :
        return [0, 1]
    
    num_pts = len(points)
    xc = points[:, [0]]
    yc = points[:, [1]]
    ones = np.ones((num_pts,1))
    X = np.concatenate((ones, xc), axis = 1)

    X_intermediary = np.dot(X.T, X)
    Y_intermediary = np.dot(X.T, yc)
    #print X_intermediary
    #print Y_intermediary

    R = np.dot( inv(X_intermediary), Y_intermediary )
    
    k = R[1][0]
    last_2 = points[-2:]
    #print last_2
    first_x = last_2[0][0]
    second_x = last_2[1][0]
    #print first_x
    
    if first_x < second_x :
        return [1, k]
    else :
        return [-1, -k]

def round_point( (x, y) ):
    return ( int(x), int(y) )

def add_points( (x1, y1), (x2, y2) ):
    return ( x1 + x2, y1 + y2 )

c = Camera()

t = BallTracker('red')
ballpos = None
while ballpos is None:
    frame = c.get_frame()
    ballpos = t.getBallCoordinates(frame)
ballpos = Tracker.transformCoordsToDecartes(ballpos)

previous_positions =  np.array( [ ballpos ] )

k = 20
while True:

    frame = c.get_frame()
    ballpos = t.getBallCoordinates(frame)
    print ballpos
    #print len(previous_positions)

    if ballpos is None:
        continue
    ballpos = Tracker.transformCoordsToDecartes(ballpos)
    previous_positions = np.append(previous_positions, [ballpos], axis = 0)

    last_k_positions = previous_positions[-k:]

    direction_vector = linear_regression(last_k_positions)
    direction_vector = [ 20 * x for x in direction_vector ]


    p1 = Tracker.transformCoordsToCV(round_point(ballpos))
    p2 = Tracker.transformCoordsToCV(round_point(add_points(ballpos, direction_vector)))
    frame = cv2.circle(frame, p1, 20, (0,0,0), 2)
    cv2.line(frame, p1, p2, (0,255,122), 2)

    cv2.imshow('frame', frame)
    l = cv2.waitKey(5) & 0xFF
    if l == 27:
        break

c.close()
cv2.destroyAllWindows()
