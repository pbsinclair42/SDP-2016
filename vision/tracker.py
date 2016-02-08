from camera import Camera
from calibrate import step
from matplotlib import pyplot as plt
import numpy as np
import cv2
from colorsHSV import *

c = Camera()

adjustments = {}
adjustments['blur'] = (19,19) # needs to be parametrized .. TODO

class Tracker():

    def get_contours(self, frame, color, adjustments):

        blur_intensity = adjustments['blur']
        blurred_frame = cv2.GaussianBlur(frame, blur_intensity, 0)
        hsv_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_frame, color_range[color][0], color_range[color][1])

        _, threshold = cv2.threshold(mask, 127, 255, 0)
        _, contours, _ = cv2.findContours(threshold, 1, 2)

        return contours

    # Extracts a center from a single contour
    def get_contour_center(self, contour):

        (cx, cy), radius = cv2.minEnclosingCircle(contour)

        return ( int(cx), int(cy) ), int(radius)


    # Extracts the centers of a list of contours
    def get_contour_centers(self, contours):

        return [ self.get_contour_center(x) for x in contours ]


    # Gives us the contour with the biggest area from a list of contours
    def get_biggest_contour(self, contours):

        max_area = -1
        max_contour_position = -1

        for i in range(0, len(contours)):
            area = cv2.contourArea(contours[i])
            if area > max_area:
                max_area = area
                max_contour_position = i

        return contours[max_contour_position]


    # Returns the distance between 2 points
    def distance(self, point_1, point_2):

        dx = ( point_1[0] - point_2[0] )
        dy = ( point_1[1] - point_2[1] )

        return dx * dx + dy * dy 


class BallTracker(Tracker):

    def __init__(self, ballColor):
        self.color = ballColor


    # Extracts the ( center, radius ) of our ball
    def get_ball_coordinates(self, frame):

        contours = self.get_contours(frame, self.color, adjustments)
        ball_contour = self.get_biggest_contour(contours)

        return self.get_contour_center(ball_contour)


    # Prints the circle around the ball onto the frame
    def show_ball_frame(self, frame):

        center, radius = self.get_ball_coordinates(frame)
        cv2.circle(frame, center, (radius+10), (255,255,255), 2)
        cv2.imshow('test', frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


class RobotTracker(Tracker):

    def __init__(self, our_color='yellow', attacker_pink = 1):

        self.side_colors = {}
        if (our_color == 'yellow'):
            self.side_colors['us'] = 'yellow'
            self.side_colors['opponent'] = 'bright_blue'
        else:
            self.side_colors['us'] = 'bright_blue'
            self.side_colors['opponent'] = 'yellow'

        self.num_pink = {}
        self.num_pink['attacker'] = attacker_pink
        self.num_pink['defender'] = 4 - attacker_pink


    # Gets the coordinates of the robot on a particular SIDE (us or opponent) and for a particular POSITION (attacker or defender)
    def get_robot_coordinates(self, frame, side, position):

        possible_opponent_contours = self.get_contours(frame, self.side_colors[side], adjustments)
        pink_contours = self.get_contours(frame, 'pink', adjustments)

        '''print self.get_contour_centers(pink_contours)
        print ('---------------')
        print self.get_contour_centers(possible_opponent_contours)'''

        #print len(pink_contours)
        for contour in possible_opponent_contours:
            contour_center, radius = self.get_contour_center(contour)
            pink_contour_count = 0

            for pink_contour in pink_contours:
                pink_contour_center, _ = self.get_contour_center(pink_contour)

                dist = self.distance( pink_contour_center, contour_center )
                if dist < 225 :
                    pink_contour_count += 1

            if pink_contour_count == self.num_pink[position]:
                return contour_center, radius

        return None


    def opponent_defender_coordinates(self, frame):
        
        return self.get_robot_coordinates(frame, 'opponent', 'defender')


    def opponent_attacker_coordinates(self, frame):
        
        return self.get_robot_coordinates(frame, 'opponent', 'attacker')


    def our_defender_coordinates(self, frame):
        
        return self.get_robot_coordinates(frame, 'us', 'defender')


    def our_attacker_coordinates(self, frame):
        
        return self.get_robot_coordinates(frame, 'us', 'attacker')   
