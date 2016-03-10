import numpy as np
import cv2
import math
from tools import *
from algebra import *

adjustments = {}
adjustments['blur'] = (11, 11)  # needs to be parametrized .. TODO
  # for PITCH=0


class Tracker():
    def denoiseMask(self, mask):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        po = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        po = cv2.morphologyEx(po, cv2.MORPH_OPEN, kernel)
        return po

    def getContours(self, frame, color, adjustments):

        color_range = get_colors()
        blur_intensity = adjustments['blur']
        blurred_frame = cv2.GaussianBlur(frame, blur_intensity, 0)
        hsv_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

        if color == 'red':
            red_mask = cv2.inRange(hsv_frame, color_range['red']['min'],
                                   color_range['red']['max'])
            maroon_mask = cv2.inRange(hsv_frame, color_range['maroon']['min'],
                                      color_range['maroon']['max'])
            mask = cv2.bitwise_or(red_mask, maroon_mask)
        else:
            mask = cv2.inRange(hsv_frame, color_range[color]['min'],
                               color_range[color]['max'])

        _, threshold = cv2.threshold(self.denoiseMask(mask), 127, 255, 0)

        _, contours, _ = cv2.findContours(threshold, 1, 2)

        return self.removeUselessContours(contours)

    def removeUselessContours(self, contours):
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

        return [self.getContourCenter(x) for x in contours]

    def getKFurthestContours(self, k, p, contours):

        distances = [distance(p, self.getContourCenter(c)) for c in contours]
        distances_sorted = np.argsort(distances)
        return [contours[x] for x in distances_sorted[-k:]]

    def getKClosestContours(self, k, p, contours):

        distances = [distance(p, self.getContourCenter(c)) for c in contours]
        distances_sorted = np.argsort(distances)

        return [contours[x] for x in distances_sorted[:k]]

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


class BallTracker(Tracker):
    def __init__(self, ball_color):
        self.color = ball_color

    # Extracts the ( center, radius ) of our ball
    def getBallCoordinates(self, frame):

        contours = self.getContours(frame, self.color, adjustments)
        if contours == []:
            return None
        ball_contour = self.getBiggestContour(contours)

        return transformCoordstoDecartes(self.getContourCenter(ball_contour))


class RobotTracker(Tracker):
    def __init__(self, ally_color='yellow'):

        self.ally_color = ally_color
        self.side_identifiers = ['yellow', 'bright_blue']

    def getAllRobots(self, frame):

        helper_contours = {}
        helper_contours['pink'] = self.getContours(frame, 'pink', adjustments)
        helper_contours['green'] = self.getContours(frame, 'green',
                                                    adjustments)

        robots = {}
        for side_color in self.side_identifiers:
            side_contours = self.getContours(frame, side_color, adjustments)
            side_robots = self.getRobotCoordinates(side_contours,
                                                   helper_contours['pink'])
            if (side_color == self.ally_color):
                robots['ally'] = side_robots
            else:
                robots['enemy'] = side_robots

        for side, side_robs in robots.iteritems():
            for color, robot in side_robs.iteritems():
                center = robot['center']
                orientation = self.getRobotOrientation(center, helper_contours,
                                                       color)
                robots[side][color]['orientation'] = orientation
                if center:
                    robots[side][color]['center'] = transformCoordstoDecartes(center)

        return robots

    def getRobotCoordinates(self, side_contours, pink_contours):

        side_robots = {'green': {"orientation": None,
                                 "center": None},
                       'pink': {"orientation": None,
                                "center": None}}
        for contour in side_contours:

            contour_center = self.getContourCenter(contour)
            pink_contour_count = 0

            for pink_contour in pink_contours:
                pink_contour_center = self.getContourCenter(pink_contour)

                dist = distance(pink_contour_center, contour_center)

                if dist < 20 * 20:
                    pink_contour_count += 1

            if pink_contour_count == 1:
                side_robots['green'] = {
                    "center": contour_center,
                    "orientation": None
                }
            elif pink_contour_count == 3:
                side_robots['pink'] = {
                    "center": contour_center,
                    "orientation": None
                }

        return side_robots

    def getRobotOrientation(self, center, helper_contours, group_color):

        magnitude = 30.0

        # print(helper_contours)

        if center is None:
            return None, None

        if group_color == 'pink':
            main_color = 'pink'
            support_color = 'green'
        else:
            main_color = 'green'
            support_color = 'pink'

        # for _, cont in helper_contours:
        #     if cont == []:
        #         return None, None
        orientation_support = self.getKClosestContours(
            1, center, helper_contours[support_color])
        support_center = self.getContourCenter(orientation_support[0])

        orientation_main = self.getKClosestContours(
            3, center, helper_contours[main_color])
        orientation_main = self.getKFurthestContours(2, support_center,
                                                     orientation_main)

        if len(orientation_main) != 2:
            return None, None

        main_centers = self.getContourCenters(orientation_main)
        # print(main_centers)
        mean_main_point = meanPoint(main_centers)

        center = transformCoordstoDecartes(center)
        mean_main_point = transformCoordstoDecartes(mean_main_point)

        direction_vector = getDirectionVector(center, mean_main_point,
                                              magnitude)
        angle_radians = np.arctan2(direction_vector[1], direction_vector[0])
        angle_degrees = math.degrees(angle_radians)

        return (angle_degrees, direction_vector)
