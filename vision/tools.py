import numpy as np
import cv2
import json
import socket
import os
import cPickle

PATH = os.path.dirname(os.path.realpath(__file__))
BLACK = (0, 0, 0)

PITCHES = ['Pitch_0', 'Pitch_1', 'Pitch_2']


def get_zones(width, height, filename=PATH+'/onfig/croppings.json', pitch=0):
    calibration = get_croppings(filename, pitch)
    zones_poly = [calibration[key] for key in ['Zone_0', 'Zone_1', 'Zone_2', 'Zone_3']]

    maxes = [max(zone, key=lambda x: x[0])[0] for zone in zones_poly[:3]]
    mins = [min(zone, key=lambda x: x[0])[0] for zone in zones_poly[1:]]
    mids = [(maxes[i] + mins[i]) / 2 for i in range(3)]
    mids.append(0)
    mids.append(width)
    mids.sort()
    return [(mids[i], mids[i+1], 0, height) for i in range(4)]


def get_croppings(filename=PATH+'/config/croppings.json', pitch=0):
    croppings = get_json(filename)
    return croppings[PITCHES[pitch]]


def get_json(filename=PATH+'/config/colors.json'):
    _file = open(filename, 'r')
    content = json.loads(_file.read())
    _file.close()
    return content


def get_radial_data(pitch=0, filename=PATH+'/config/undistort.txt'):
    _file = open(filename, 'r')
    data = cPickle.load(_file)
    _file.close()
    return data[pitch]


def get_colors(filename=PATH+'/config/colors.json'):
    """
    Get colros from the JSON calibration file.
    Converts all
    """
    json_content = get_json(filename)
    machine_name = socket.gethostname().split('.')[0]

    if machine_name in json_content:
        current = json_content[machine_name]
    else:
        current = json_content['default']

    # convert mins and maxes into np.array
    for key in current:
        key_dict = current[key]
        if 'min' in key_dict:
            key_dict['min'] = np.array(tuple(key_dict['min']))
        if 'max' in key_dict:
            key_dict['max'] = np.array(tuple(key_dict['max']))

    return current


def save_colors(colors, filename=PATH+'/config/colors.json'):
    #json_content = get_json(filename)
    #machine_name = "default"
    machine_name = socket.gethostname().split('.')[0]
    print filename
    print machine_name
    # now that we have the feed settings set by v4lctl, should be no need to store calibrations
    # from different pcs
    print colors
    # convert np.arrays into lists
    for key in colors:
        key_dict = colors[key]
        if 'min' in key_dict:
            key_dict['min'] = list(key_dict['min'])
        if 'max' in key_dict:
            key_dict['max'] = list(key_dict['max'])

    with open(filename, "r+") as jsonFile:
        data = json.load(jsonFile)
        if machine_name in data:
            data[machine_name] = colors
            print "Updating JSON file"
        else:
            data[machine_name] = data['default']
            data[machine_name] = colors
        print "DATA:" 
        for comp_name in data: 
            print comp_name + ":"   
            print data[comp_name]    
        print "Writing into a file"    
        jsonFile.seek(0)  # rewind
        jsonFile.write(json.dumps(data, indent=4))
        jsonFile.truncate()
    #write_json(filename, json_content)


def save_croppings(pitch, data, filename=PATH+'/config/croppings.json'):
    """
    Open the current croppings file and only change the croppings
    for the relevant pitch.
    """
    croppings = get_json(filename)
    croppings[PITCHES[pitch]] = data
    write_json(filename, croppings)


def write_json(filename=PATH+'/config/colors.json', data={}):
    _file = open(filename, 'w')
    _file.write(json.dumps(data, indent=4))
    _file.close()


def mask_pitch(frame, points):
    mask = frame.copy()
    points = np.array(points, np.int32)
    cv2.fillConvexPoly(mask, points, BLACK)
    hsv_mask = cv2.cvtColor(mask, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_mask, (0, 0, 0), (0, 0, 0))
    return cv2.bitwise_and(frame, frame, mask=mask)


def find_extremes(coords):
    left = min(coords, key=lambda x: x[0])[0]
    right = max(coords, key=lambda x: x[0])[0]
    top = min(coords, key=lambda x: x[1])[1]
    bottom = max(coords, key=lambda x: x[1])[1]
    return (left, right, top, bottom)


def find_crop_coordinates(frame, keypoints=None, width=520, height=285):
    """
    Get crop coordinated for the actual image based on masked version.

    Params:
        [int] width     fixed width of the image to crop to
        [int[ height    fixed height of the image to crop to

    Returns:
        A 4-tuple with crop values
    """
    frame_height, frame_width, channels = frame.shape
    if frame_width < width or frame_height < height:
        print 'get_crop_coordinates:', 'Requested size of the frame is smaller than the original frame'
        return frame

    if not keypoints:
        # Smoothen and apply white mask
        mask = mask_field(normalize(frame))

        # Get FAST detection of features
        fast = cv2.FastFeatureDetector()

        # get keypoints - list of Keypoints with x/y coordinates
        kp = fast.detect(mask, None)

        x_min = min(kp, key=lambda x: x.pt[0]).pt[0]
        y_min = min(kp, key=lambda x: x.pt[1]).pt[1]
        x_max = max(kp, key=lambda x: x.pt[0]).pt[0]
        y_max = max(kp, key=lambda x: x.pt[1]).pt[1]

    else:
        x_min = min(keypoints, key=lambda x: x[0])[0]
        y_min = min(keypoints, key=lambda x: x[1])[1]
        x_max = max(keypoints, key=lambda x: x[0])[0]
        y_max = max(keypoints, key=lambda x: x[1])[1]

    x_delta = x_max - x_min
    y_delta = y_max - y_min

    # x_remaining = max(0, (width - x_delta) / 2)
    # y_remaining = max(0, (height - y_delta) / 2)

    return (
        x_min, x_max,
        y_min, y_max)


def crop(frame, size=None):
    """
    Crop a frame given the size.
    If size not provided, attempt to extract the field and crop.

    Params:
        [OpenCV Frame] frame    frame to crop
        [(x1,x2,y1,y2)] size
    """
    # if not size or not len(size):
    #     x_min, x_max, y_min, y_max = get_crop_coordinates(frame)
    # else:
    # print 'SIZE:', size
    x_min, x_max, y_min, y_max = size
    return frame[y_min:y_max, x_min:x_max]
