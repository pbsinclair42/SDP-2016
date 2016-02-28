from camera import Camera
from calibrate import step
from matplotlib import pyplot as plt
from socket import gethostname
import numpy as np
import cv2
import math
from tools import *
#from colorsHSV import *

# get computer name

adjustments = {}
adjustments['blur'] = (11,11) # needs to be parametrized .. TODO
color_range = get_colors(0) #for PITHC=0

class Tracker():

    def denoiseMask(self, mask):
        kernel =  cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
        po = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        po = cv2.morphologyEx(po, cv2.MORPH_OPEN, kernel)
        return po

    def getContours(self, frame, color, adjustments):

        blur_intensity = adjustments['blur']
        blurred_frame = cv2.GaussianBlur(frame, blur_intensity, 0)
        hsv_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

        if color == 'red':
            red_mask = cv2.inRange(hsv_frame, color_range['red']['min'], color_range['red']['max'])
            maroon_mask = cv2.inRange(hsv_frame, color_range['maroon']['min'], color_range['maroon']['max'])
            mask = cv2.bitwise_or(red_mask, maroon_mask)
        else:
            mask = cv2.inRange(hsv_frame, color_range[color]['min'], color_range[color]['max'])

        _, threshold = cv2.threshold(self.denoiseMask(mask), 127, 255, 0)

        _, contours, _ = cv2.findContours(threshold, 1, 2)

        return self.removeUselessContours(contours)

    def removeUselessContours( self, contours ) :
        if contours is None:
            return None
        real_contours = []
        for contour in contours:
            _, radius = cv2.minEnclosingCircle(contour)
            if radius > 1.3 and radius < 20:
                real_contours.append(contour)

        return real_contours

    # Extracts a center from a single contour
    def getContourCenter(self, contour):
        if contour is None:
            return None
        center, _ = cv2.minEnclosingCircle(contour)
        return center


    # Extracts the centers of a list of contours
    def getContourCenters(self, contours):

        return [ self.getContourCenter(x) for x in contours ]


    def getKFurthestContours(self, k, p, contours):

        distances = [ self.distance( p, self.getContourCenter(c) ) for c in contours ]
        distances_sorted = np.argsort(distances)
        return [ contours[x] for x in distances_sorted[-k:] ]


    def getKClosestContours(self, k, p, contours):

        distances = [ self.distance( p, self.getContourCenter(c) ) for c in contours ]
        distances_sorted = np.argsort(distances)

        return [ contours[x] for x in distances_sorted[:k]]


    # Gives us the contour with the biggest area from a list of contours
    def getBiggestContour(self, contours):

        max_area = -1
        max_contour_position = -1

        if len(contours) == 0:
            return None

        for i in range(0, len(contours)):
            area = cv2.contourArea(contours[i])
            if area > max_area:
                max_area = area
                max_contour_position = i

        return contours[max_contour_position]


    # Returns the distance between 2 points
    @staticmethod
    def distance(point_1, point_2):

        dx = ( point_1[0] - point_2[0] )
        dy = ( point_1[1] - point_2[1] )

        return dx * dx + dy * dy


    def meanPoint(self, points):

        tx = 0.0
        ty = 0.0

        for point in points:
            tx += point[0]
            ty += point[1]

        l = len(points)
        if l == 0:
            return None

        return ( tx / l, ty / l )


    def getDirectionVector( self, (cx, cy), (ox, oy) ):

        diff_x = cx - ox
        diff_y = cy - oy

        if diff_x == 0:
            return (0, -diff_x)

        k = (cy - oy) / (cx - ox)

        if ox >= cx :
            dir_vector = [1, k]
        else :
            dir_vector = [-1, -k]

        return dir_vector


    def rotateVector( self, (x, y), angle ):
        x_new = x * math.cos(angle) - y * math.sin(angle)
        y_new = x * math.sin(angle) + y * math.cos(angle)

        return [x_new, y_new]

    @staticmethod
    def transformCoordstoDecartes( (x, y) ):
        return ( x - 320, 240 - y )

    @staticmethod
    def transformCoordstoCV( (x, y) ) :
        return ( x + 320, 240 - y )


class BallTracker(Tracker):

    def __init__(self, ball_color):
        self.color = ball_color


    # Extracts the ( center, radius ) of our ball
    def getBallCoordinates(self, frame):

        contours = self.getContours(frame, self.color, adjustments)
        if contours is None:
            return None
        ball_contour = self.getBiggestContour(contours)

        return self.getContourCenter(ball_contour)


class RobotTracker(Tracker):

    def __init__(self, our_color='yellow', num_of_pink = 1):

        self.side_colors = {}
        if (our_color == 'yellow'):
            self.side_colors['us'] = 'yellow'
            self.side_colors['opponent'] = 'bright_blue'
        else:
            self.side_colors['us'] = 'bright_blue'
            self.side_colors['opponent'] = 'yellow'

        self.num_pink = {}
        if num_of_pink == 1:
            self.num_pink['pink_robot'] = 4 - num_of_pink
            self.num_pink['green_robot'] = num_of_pink
        else:
            self.num_pink['pink_robot'] = num_of_pink
            self.num_pink['green_robot'] = 4 - num_of_pink


    # Gets the coordinates of the robot on a particular SIDE (us or opponent) and for a particular POSITION (attacker or defender)
    def getRobotCoordinates(self, frame, side, position):

        side_contours = self.getContours(frame, self.side_colors[side], adjustments)
        pink_contours = self.getContours(frame, 'pink', adjustments)

        for contour in side_contours:

            contour_center = self.getContourCenter(contour)
            pink_contour_count = 0

            for pink_contour in pink_contours:
                pink_contour_center = self.getContourCenter(pink_contour)

                dist = self.distance( pink_contour_center, contour_center )

                if dist < 20*20 :
                    pink_contour_count += 1

            if pink_contour_count == self.num_pink[position]:
                return contour_center

        return None


    def getRobotOrientation(self, frame, side, position):

        center = self.getRobotCoordinates(frame, side, position)
        if center is None:
            return None, None

        if self.num_pink[position] == 3:

            green_contours = self.getContours(frame, 'green', adjustments)
            pink_contours = self.getContours(frame, 'pink', adjustments)

            if green_contours == []:
                return None, None

            orientation_green = self.getKClosestContours(1, center, green_contours)

            green_center = self.getContourCenter(orientation_green[0])

            orientation_pink = self.getKClosestContours(3, green_center, pink_contours)
            orientation_pink = self.getKFurthestContours(2, green_center, orientation_pink)
            if len(orientation_pink) != 2:
                return None, None

            pink_centers = self.getContourCenters(orientation_pink)
            mean_pink_point = self.meanPoint(pink_centers)

            center = self.transformCoordstoDecartes( center )
            mean_pink_point = self.transformCoordstoDecartes( mean_pink_point )
            direction_vector = self.getDirectionVector(center, mean_pink_point)

            angle_radians = np.arctan2( direction_vector[1], direction_vector[0] )
            angle_degrees = math.degrees( angle_radians )

        else:

            pink_contours = self.getContours(frame, 'pink', adjustments)
            orientation_pink = self.getKClosestContours(1, center, pink_contours)

            if orientation_pink == []:
                return None, None

            pink_center = self.getContourCenter(orientation_pink[0])

            center = self.transformCoordstoDecartes(center)
            pink_center = self.transformCoordstoDecartes( pink_center )

            direction_vector = self.getDirectionVector( center, pink_center )
            direction_vector = self.rotateVector( direction_vector, math.radians(215) )

            angle_radians = np.arctan2( direction_vector[1], direction_vector[0] )
            angle_degrees = math.degrees(angle_radians)

        return (angle_degrees, direction_vector), center


    def opponent_green_coordinates(self, frame):

        return self.getRobotCoordinates(frame, 'opponent', 'green_robot')


    def opponent_pink_coordinates(self, frame):

        return self.getRobotCoordinates(frame, 'opponent', 'pink_robot')


    def our_green_coordinates(self, frame):

        return self.getRobotCoordinates(frame, 'us', 'green_robot')


    def our_pink_coordinates(self, frame):

        return self.getRobotCoordinates(frame, 'us', 'pink_robot')
