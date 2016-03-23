import numpy as np
import cv2
import math
from tools import *
from algebra import *
from array_queue import ArrayQueue
from vector import Vector

adjustments = {}
adjustments['blur'] = (11, 11)  # needs to be parametrized .. TODO
color_range = get_colors()  # for PITCH=0


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


    def getMultiColorContours(self, frame, color_list):
        all_contours = []
        for color in color_list:
            tmp_contours = self.getContours(frame, color, adjustments)

            # Gets the (CENTER, color) of the contours, not the list of contour object
            processed_contours = [(x, color) for x in self.getContourCenters(tmp_contours)]
            all_contours += processed_contours

        return all_contours

    def removeUselessContours(self, contours):
        if contours is None:
            return None
        real_contours = []
        for contour in contours:
            _, radius = cv2.minEnclosingCircle(contour)
            if radius > 1.3 and radius < 15:
                real_contours.append(contour)

        return real_contours

    # Extracts a center from a single contour
    def getContourCenter(self, contour):
        if contour is None:
            return None
        center, _ = cv2.minEnclosingCircle(contour)
        # print center
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

        return self.getContourCenter(ball_contour)


class RobotTracker(Tracker):
    def __init__(self, ally_color = 'yellow', me_color = 'green', max_queue_size = 10):

        self.ally_color = ally_color
        self.side_identifiers = ['yellow', 'bright_blue']
        self.robot_identifiers = ['pink', 'green']
        self.all_colors = self.side_identifiers + self.robot_identifiers
        self.previous_locations = {}
        self.previous_orientations = {}

        combinations = self.colorCombinations()
        for c in combinations:
            self.previous_locations[c] = ArrayQueue(max_queue_size)
        for c in combinations:
            self.previous_orientations[c] = ArrayQueue(max_queue_size)

        self.color_map = {}
        self.color_map[self.ally_color] = 'ally'
        self.color_map[self.opposingColor(self.ally_color)] = 'enemy'
        self.color_map[me_color] = 'me'
        self.color_map[self.opposingColor(me_color)] = 'friend'


    def opposingColor(self, c):
        opposing_color = {'yellow':'bright_blue', 'bright_blue':'yellow',
                          'pink':'green', 'green':'pink'}
        return opposing_color[c]

    def mapColorToRealClassification(self, (s, r)):

        return (self.color_map[s], self.color_map[r])


    def colorCombinations(self):

        combinations = [(x, y) for x in self.side_identifiers for y in self.robot_identifiers]
        return combinations

    def identifierCombinations(self):
        combs = self.colorCombinations()
        real_combs = [ self.mapColorToRealClassification(x) for x in combs ]
        return real_combs

    def groupContours(self,contour_list):

        buckets = []

        l = len(contour_list)
        processed = [False] * l

        for i in range(l):

            bucket_tmp = []
            center, color = contour_list[i]
            if color in self.side_identifiers:
                #print "Enter"
                bucket_tmp.append( (center, color) )
                processed[i] = True
                for j in range(l):
                    if i == j:
                        continue
                    if processed[j]:
                        continue

                    support_center, support_color = contour_list[j]
                    dist = distance(center, support_center)
                    if dist < 20 * 20:
                        bucket_tmp.append( (support_center, support_color) )
                        processed[j] = True

                buckets.append(bucket_tmp)


        for i in range(l):

            if processed[i]:
                continue

            bucket_tmp = []
            center, color = contour_list[i]
            bucket_tmp.append( (center, color) )
            for j in range(l):
                if i == j:
                    continue
                if processed[j]:
                    continue

                support_center, support_color = contour_list[j]
                dist = distance(center, support_center)
                if dist < 30 * 30:
                    bucket_tmp.append( (support_center, support_color) )
                    processed[j] = True

                #if len(bucket_tmp) <= 5:
            buckets.append(bucket_tmp)


        return (buckets, len(buckets))


    def classifyBuckets(self, buckets):

        combinations = self.colorCombinations()
        # print combinations
        num_buckets = len(buckets)
        possibilities = [combinations] * num_buckets
        bucket_classifications = {}
        for c in combinations:
            bucket_classifications[c] = None

        classifications_done = 0

        # Elimination of bad classifications
        changed = True
        while changed and classifications_done < 4:
            changed = False
            for i in range(num_buckets):
                num = {}
                for color in self.all_colors:
                    num[color] = len([x for (_, x) in buckets[i] if x == color])

                for side_color in self.side_identifiers:
                    if num[side_color] == 1:
                        opposing_col = self.opposingColor(side_color)
                        possibilities[i] = [ (a,b) for (a,b) in possibilities[i] if a != opposing_col ]

                for robot_color in self.robot_identifiers:
                    if num[robot_color] > 1:
                        opposing_col = self.opposingColor(robot_color)
                        possibilities[i] = [ (a,b) for (a,b) in possibilities[i] if b != opposing_col ]


            for i in range(num_buckets):
                pos_len = len(possibilities[i])
                if pos_len == 0:
                    print "Bucketing is fucked up"
                elif pos_len == 1:
                    # This is the case that we want
                    classification = possibilities[i][0]
                    bucket_classifications[classification] = buckets[i]
                    classifications_done += 1
                    for j in range(num_buckets):
                        possibilities[j] = [x for x in possibilities[j] if x != classification]

                    changed = True

        return bucket_classifications


    def gradientDescent(self, bucket):

        ''' needs some more thinking, not sure if an actual gradient descent is superior '''
        points = [x for (x, _) in bucket]

        return meanPoint(points)


    def calculateLocation(self, classification, bucket):

        # Can only happen if >= 2 contours in the bucket

        for center, color in bucket:
            if color in self.side_identifiers:
                return center

        return self.gradientDescent(bucket)


    def estimatePositions(self, bucket_classifications):

        combinations = self.colorCombinations()
        estimated_locations = {}
        for c in combinations:
            estimated_locations[c] = self.calculateLocation(c, bucket_classifications[c])
            self.previous_locations[c].insert(estimated_locations[c])

        return estimated_locations

    def calculateLocation(self, robot_classification, bucket):

        ''' If the location can be taken from the bucket, return the mean '''
        if bucket is not None and len(bucket) > 1:
            points = [x for (x, _) in bucket]
            return meanPoint(points)

        if not self.previous_locations[robot_classification].full():
            return None

        ''' Get the ArrayQueue(previous locations) for robot with the 'key' identifier '''
        points_queue = self.previous_locations[robot_classification]
        trajectory_vector = linear_regression(points_queue)

        if trajectory_vector is None:
            return None

        trajectory_vector.rescale(1)
        speed = self.getSpeed(robot_classification)
        dislocation = Vector.scalarMultiple(trajectory_vector, speed)

        prev_location = points_queue.getLeft()
        estimated_robot_position = Vector.addToPoint( prev_location, dislocation )

        return estimated_robot_position



    ''' Measures speed in distance/frame '''
    def getSpeed(self, key):

        points_queue = self.previous_locations[key]
        if not points_queue.full():
            return None

        beginning_p = points_queue.getRight()
        end_p = points_queue.getLeft()

        size = points_queue.getMaxSize()
        speed = distance(beginning_p, end_p) ** (0.5) / size

        return speed


    def estimateOrientations(self, bucket_classifications,  estimated_positions):

        combinations = self.colorCombinations()
        estimated_orientations = {}
        # for c in combinations:
        #     estimated_orientations[c] = None, None

        for key, center in estimated_positions.iteritems():
            # print "Key:", key
            if center is None:
                estimated_orientations[key] = None
                continue
            side_color, main_color = key
            support_color = self.opposingColor(main_color)


            support_orientation_vector = None
            final_vector = None

            if self.previous_orientations[key].full():
                support_orientation_vector = self.previous_orientations[key].getLeft()

            # bucket_index = self.findBucket(buckets, bucket_classifications, key, num_buckets)
            # if bucket_index == -1:
            #     final_vector = support_orientation_vector
            #     self.updateOrientations(estimated_orientations, final_vector, key)
            #     continue

            bucket_key = bucket_classifications[key]
            if bucket_key is None:
                #print "takes previous vector"
                final_vector = support_orientation_vector
                self.updateOrientations(estimated_orientations, final_vector, key)
                continue


            for bucket_center, bucket_color in bucket_key:
                if bucket_color == support_color:
                    #print "ENTER--------------"
                    support_orientation_vector = Vector.getDirectionVector( bucket_center, center, 1 )
                    support_orientation_vector.rotate(math.radians(215))

            if support_orientation_vector is None:
                final_vector = None
                self.updateOrientations(estimated_orientations, final_vector, key)
                continue

            centers_main_color = [ x for (x, c) in bucket_key if c == main_color ]
            centers_len = len(centers_main_color)

            midpoints_main_color = []
            for i in range(centers_len - 1):
                for j in range(i+1, centers_len):
                    center_i = centers_main_color[i]
                    center_j = centers_main_color[j]
                    midpoints_main_color.append( meanPoint([center_i, center_j]) )

            dvs_main_color = [ Vector.getDirectionVector(x, center, 10) for x in midpoints_main_color]
            dvs_len = len(dvs_main_color)

            if dvs_len < 2:
                final_vector = support_orientation_vector
                self.updateOrientations(estimated_orientations, final_vector, key)
                continue



            angle_min = 999999
            vector_min = None
            for v in dvs_main_color:

                if support_orientation_vector.toPoint() == (0, 0) or v.toPoint() == (0,0):
                    self.updateOrientations(estimated_orientations, None, key)
                    continue

                angle_tmp = abs(Vector.angleBetween(support_orientation_vector, v))
                if angle_tmp < angle_min:
                    angle_min = angle_tmp
                    vector_min = v

            angle_check = abs(Vector.angleBetween(vector_min, support_orientation_vector))
            if angle_check < 20:
                final_vector = vector_min
            else:
                final_vector = support_orientation_vector

            self.updateOrientations(estimated_orientations, final_vector, key)
            self.previous_orientations[key].insert(final_vector)

        return estimated_orientations


    def findBucket(self, buckets, bucket_classifications, key, numbuckets):

        # print bucket_classifications
        if bucket_classifications is None:
            return -1
        # real_classification_tmp = [ (self.color_map[x], y) for (x,y) in bucket_classifications ]
        real_classification_tmp = []
        for c in bucket_classifications:
            if c is None:
                real_classification_tmp.append(None)
                continue
            x,y = c
            real_classification_tmp.append((self.color_map[x], y))

        for index, bucket_key in zip([i for i in range(numbuckets)], real_classification_tmp):
            if bucket_key == key:
                return index

        return -1



    def updateOrientations(self, estimated_orientations, v, key):

        if v is None:
            estimated_orientations[key] = None
            return

        v.switchCoords()
        tmp = v.toPoint()
        angle_radians = np.arctan2(tmp[1], tmp[0])
        angle_degrees = math.degrees(angle_radians)

        v.switchCoords()
        v.rescale(50)
        estimated_orientations[key] = v.toPoint(), angle_degrees



    def getRobotParameters(self, frame):

        all_contours = self.getMultiColorContours(frame, self.all_colors)
        buckets, bucket_counter = self.groupContours(all_contours)
        print "Bucket counter: ", bucket_counter
        for bucket in buckets:
            print "Bucket -----> ", bucket
        # print "Buckets: "
        # for i in range(4):
        #     print "Bucket ----> ", i
        #     print buckets[i]
        # for bucket in buckets:
        #     print bucket

        bucket_classifications = self.classifyBuckets(buckets)
        estimated_locations = self.estimatePositions(bucket_classifications)
        estimated_orientations = self.estimateOrientations(bucket_classifications, estimated_locations)

        # print "Classifications: ", bucket_classifications

        # print "Locations: ", estimated_locations
        # print "Orientations: ", estimated_orientations

        robots_all = {}
        for key in self.colorCombinations():
            real_key = self.mapColorToRealClassification(key)
            robots_all[real_key] = {}

        for key in self.colorCombinations():
            real_key = self.mapColorToRealClassification(key)
            robots_all[real_key]['center'] = estimated_locations[key]
            robots_all[real_key]['orientation'] = estimated_orientations[key]

        return robots_all

