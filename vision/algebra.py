import math

def distance(point_1, point_2):

    dx = ( point_1[0] - point_2[0] )
    dy = ( point_1[1] - point_2[1] )

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


def getVectorMagnitude(v):

    return (v[0] ** 2 + v[1] ** 2) ** (0.5)


def getDirectionVector( (cx, cy), (ox, oy), length ):

    diff_x = cx - ox
    diff_y = cy - oy

    if diff_x == 0:
        return (0, -diff_x)

    k = (cy - oy) / (cx - ox)

    if ox >= cx :
        dir_vector = [1, k]
    else :
        dir_vector = [-1, -k]

    current_magnitude = getVectorMagnitude(dir_vector)
    dir_vector = [ x * (length/current_magnitude) for x in dir_vector ]
    return dir_vector


def rotateVector( (x, y), angle ):
    x_new = x * math.cos(angle) - y * math.sin(angle)
    y_new = x * math.sin(angle) + y * math.cos(angle)

    return [x_new, y_new]

def transformCoordstoDecartes( (x, y) ):
    return ( x - 320, 240 - y )

def transformCoordstoCV( (x, y) ) :
    return ( x + 320, 240 - y )

