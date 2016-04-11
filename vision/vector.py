''' 2D Vector classic implementing the basic vector functionality '''

import math
from algebra import *


class Vector():

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def toPoint(self):
        return (self.x, self.y)

    def magnitude(self):
        return (self.x ** 2 + self.y ** 2) ** (0.5)

    def rotate(self, angle):
        self.switchCoords()
        x = self.x
        y = self.y
        self.x = x * math.cos(angle) - y * math.sin(angle)
        self.y = x * math.sin(angle) + y * math.cos(angle)
        self.switchCoords()

    def rescale(self, desired_magnitude):
        mag_tmp = self.magnitude()
        if mag_tmp != 0:
            self.x = self.x * desired_magnitude / mag_tmp
            self.y = self.y * desired_magnitude / mag_tmp

    def isZero(self):
        return self.x == 0 and self.y == 0

    def copy(self):
        return Vector(self.x, self.y)

    def switchCoords(self):
        self.y = - self.y

    @staticmethod
    def dotProduct(v1, v2):
        return v1.x * v2.x + v1.y * v2.y

    @staticmethod
    def angleBetween(v1, v2):

        dot_prod = Vector.dotProduct(v1, v2)
        cos_alpha = dot_prod / (v1.magnitude() * v2.magnitude())

        if cos_alpha > 1.0:
            cos_alpha = 1.0
        if cos_alpha < -1.0:
            cos_alpha = -1.0

        alpha = math.acos(cos_alpha)

        return math.degrees(alpha)

    @staticmethod
    def transformCoordstoDecartes( (x, y) ):
        return ( x - 320, 240 - y )
    @staticmethod
    def getDirectionVector( (cx, cy), (ox, oy), desired_magnitude ):

        (cx_d, cy_d) = Vector.transformCoordstoDecartes((cx, cy))
        (ox_d, oy_d) = Vector.transformCoordstoDecartes((ox, oy))
        diff_x = cx_d - ox_d
        diff_y = cy_d - oy_d

        if diff_x == 0:
            return Vector(0, -diff_y)

        # k = diff_y / diff_x
        # if ox_d >= cx_d :
        #     dir_vector = Vector(1, k)
        # else :
        #     dir_vector = Vector(-1, -k)
        dir_vector = Vector(diff_x, diff_y)

        dir_vector.switchCoords()
        dir_vector.rescale(desired_magnitude)

        return dir_vector

    @staticmethod
    def scalarMultiple(v, c):
        return Vector(v.x * c, v.y * c)
    @staticmethod
    def addToPoint((px, py), v):
        return (px + v.x, py + v.y)

