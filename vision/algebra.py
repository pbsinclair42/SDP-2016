import math
import numpy as np
from vector import Vector
from array_queue import ArrayQueue
from numpy.linalg import inv

def distance(point_1, point_2):

    dx = ( point_1[0] - point_2[0] )
    dy = ( point_1[1] - point_2[1] )

    '''Not the mathematical distance, but
    root is an expensive op, and we don't really need it'''
    return dx * dx + dy * dy


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


def transformCoordstoDecartes( (x, y) ):
    return ( x - 320, 240 - y )

def transformCoordstoCV( (x, y) ) :
    return ( x + 320, 240 - y )

def linear_regression(points_queue):

    points = points_queue.iteritems()
    #print "Points -----> ", points

    if None in points:
        return None # Might need revisiting 

    points = list(set(points))

    if distance(points[0], meanPoint(points)) < 200:
        return Vector(0, 0)

    num_pts = len(points)
    print num_pts
    # M = np.array([points[0]])
    # for i in range(1, num_pts):
    #     print points[i]
    #     M = np.append(M, [points[i]], axis=0)
    #     print M

    descartes_points = [ transformCoordstoDecartes(x) for x in points ]
    M = np.array( [[a, b] for (a, b) in descartes_points] )
    print  "M ---------->", M
    xc = M[:, [0]]
    print "Xc --------->", xc
    yc = M[:, [1]]
    print "Yc --------->", yc
    ones = np.ones((num_pts, 1))
    X = np.concatenate((ones, xc), axis=1)

    X_intermediary = np.dot(X.T, X)
    Y_intermediary = np.dot(X.T, yc)

    R = np.dot(inv(X_intermediary), Y_intermediary)

    k = R[1][0]

    beginning_x = points_queue.getRight()[0]
    end_x = points_queue.getLeft()[0]

    final_vector = Vector(1, k)

    ''' If the direction of the robot is negative in the x-axis, flip the vector over y = x '''
    if beginning_x > end_x:
        final_vector = Vector.scalarMultiple(final_vector, -1)

    # if beginning_x < end_x:
    #     final_vector = Vector(1, k)
    # else:
    #     final_vector = Vector(-1, -k)

    final_vector.switchCoords()
    return final_vector
