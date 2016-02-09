from camera import Camera
from calibrate import step
from matplotlib import pyplot as plt
from socket import gethostname
import numpy as np
import cv2
import math
from colorsHSV import *

# get computer name
computer_name = gethostname().split('.')[0]

adjustments = {}
adjustments['blur'] = (11,11) # needs to be parametrized .. TODO

class Tracker():

    def get_contours(self, frame, color, adjustments):

        blur_intensity = adjustments['blur']
        blurred_frame = cv2.GaussianBlur(frame, blur_intensity, 0)
        hsv_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)
        if color == 'red':
            red_mask = cv2.inRange(hsv_frame, color_range[(computer_name,'red')][0], color_range[(computer_name,'red')][1])
            maroon_mask = cv2.inRange(hsv_frame, color_range[(computer_name,'maroon')][0], color_range[(computer_name,'maroon')][1])
            mask = cv2.bitwise_or(red_mask, maroon_mask)
        else:    
            mask = cv2.inRange(hsv_frame, color_range[(computer_name,color)][0], color_range[(computer_name,color)][1])

        _, threshold = cv2.threshold(mask, 127, 255, 0)
        _, contours, _ = cv2.findContours(threshold, 1, 2)

        return contours

    # Extracts a center from a single contour
    def get_contour_center(self, contour):

        (cx, cy), radius = cv2.minEnclosingCircle(contour)
        #print radius

        return ( cx, cy ), radius


    # Extracts the centers of a list of contours
    def get_contour_centers(self, contours):

        return [ self.get_contour_center(x) for x in contours ]

    def getK_furthest_contours(self, k, p, contours):
        ##print len(contours)
        ##print contours
        distances = [ self.distance( p[0], self.get_contour_center(c)[0] ) for c in contours]
        distances_sorted = np.argsort(distances)
        ##print distances
        ##print distances_sorted
        return [ contours[x] for x in distances_sorted[-k:]]

    def getK_closest_contours(self, k, p, contours):#

        distances = [ self.distance( p[0], self.get_contour_center(c)[0] ) for c in contours]
        #print 80 * "="
        #print distances
        distances_sorted = np.argsort(distances)
        #print 80 * "="
        #print distances_sorted
        #print [ contours[x] for x in distances_sorted[:k]]
        return [ contours[x] for x in distances_sorted[:k]]


    # Gives us the contour with the biggest area from a list of contours
    def get_biggest_contour(self, contours):

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
    def distance(self, point_1, point_2):

        dx = ( point_1[0] - point_2[0] )
        dy = ( point_1[1] - point_2[1] )

        return dx * dx + dy * dy 

    def average_point(self, points):

        tx = 0.0
        ty = 0.0

        for point in points:
            tx += point[0]
            ty += point[1]

        l = len(points)

        return ( tx / l, ty / l )

    def getDirectionVector( self, center, orientation_p ):

        (cx, cy) = center
        (ox, oy) = orientation_p

        k = (cy - oy) / (cx - ox)

        t  = 10

        if ox < cx :
            t = -10

        dv = (1, k)

        return [ t * x for x in dv ]

    def rotateVector( self, (x, y), angle ):
        x_new = x * math.cos(angle) - y * math.sin(angle)
        y_new = x * math.sin(angle) + y * math.cos(angle)

        return [x_new, y_new]
    
    @staticmethod
    def transformCoordstoDecartes( (x, y) ):
        return ( x - 320, -y + 240 )

    @staticmethod
    def transformCoordstoCV( (x, y) ) :
        return ( x + 320, 240 - y )

class BallTracker(Tracker):

    def __init__(self, ballColor):
        self.color = ballColor


    # Extracts the ( center, radius ) of our ball
    def get_ball_coordinates(self, frame):

        contours = self.get_contours(frame, self.color, adjustments)
        ball_contour = self.get_biggest_contour(contours)

        return self.get_contour_center(ball_contour)

    ## Prints the circle around the ball onto the frame
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

        #'''print self.get_contour_centers(pink_contours)
        #print ('---------------')
        #print self.get_contour_centers(possible_opponent_contours)'''

        print len(possible_opponent_contours)

        for contour in possible_opponent_contours:
            contour_center, radius = self.get_contour_center(contour)
            pink_contour_count = 0
            if radius < 2 or radius > 15:
                continue
            for pink_contour in pink_contours:
                pink_contour_center, radius = self.get_contour_center(pink_contour)

                if radius < 2 or radius > 15:
                    continue

                dist = self.distance( pink_contour_center, contour_center )
                if dist < 20*20 :
                    pink_contour_count += 1
            print("Pink: ", pink_contour_count)

            if pink_contour_count == self.num_pink[position]:
                return contour_center, radius

        return None

    def get_robot_orientation(self, frame, side, position):

        center = self.get_robot_coordinates(frame, side, position)

        if self.num_pink[position] == 3:
            orientation_color = 'pink'
            pass
        else:
            orientation_color = 'bright_green'

            orientation_contours_pink = self.get_contours(frame, 'pink', adjustments)
            #orientation_contours_green = self.get_contours(frame, 'bright_green', adjustments)

            pink_contour = self.getK_closest_contours(1, center, orientation_contours_pink)


            pink_center = self.get_contour_center(pink_contour[0])

            center = self.transformCoordstoDecartes(center[0])

            #closest_green = self.getK_closest_contours(1, pink_center, orientation_contours_green)
            pink_center = self.transformCoordstoDecartes( pink_center[0] )
            #green_center = self.get_contour_center(closest_green[0])
            #green_center = self.transformCoordstoDecartes( green_center[0] )
            #midpoint = self.average_point( [pink_center, green_center] )

            #print("Center: ", center)
            #print("Midpoint", midpoint)
            direction_vector1 = self.getDirectionVector( center, pink_center )
            direction_vector2 = self.rotateVector( direction_vector1, math.radians(205) )
            
            print ('Direction Vector1:', direction_vector1)
            print ('Direction Vector2:', direction_vector2)

            angle_radians = np.arctan2( direction_vector2[1], direction_vector2[0] )
            angle_degrees = math.degrees(angle_radians)

        return angle_degrees, direction_vector1, direction_vector2


    def opponent_defender_coordinates(self, frame):
        
        return self.get_robot_coordinates(frame, 'opponent', 'defender')


    def opponent_attacker_coordinates(self, frame):
        
        return self.get_robot_coordinates(frame, 'opponent', 'attacker')


    def our_defender_coordinates(self, frame):
        
        return self.get_robot_coordinates(frame, 'us', 'defender')


    def our_attacker_coordinates(self, frame):
        
        return self.get_robot_coordinates(frame, 'us', 'attacker')   
