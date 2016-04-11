import numpy as np
import cv2
import json
import socket
import os
import cPickle

PATH = os.path.dirname(os.path.realpath(__file__))

def read_json(file):
    with open(file, "r") as f:
        return json.loads(f.read())

def get_json(filename=PATH+'/config/colors.json'):
    _file = open(filename, 'r')
    content = json.loads(_file.read())
    _file.close()
    return content

'''
def get_radial_data(pitch=0, filename=PATH+'/config/undistort.txt'):
    _file = open(filename, 'r')
    data = cPickle.load(_file)
    _file.close()
    return data[pitch]
'''

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
    data = get_json(filename)
    machine_name = socket.gethostname().split('.')[0]
    # convert np.arrays into lists
    for key in colors:
        key_dict = colors[key]
        if 'min' in key_dict:
            key_dict['min'] = list(key_dict['min'])
        if 'max' in key_dict:
            key_dict['max'] = list(key_dict['max'])

    if machine_name in data:
            data[machine_name] = colors
    else:
        data[machine_name] = data['default']
        data[machine_name] = colors        

    write_json(filename, data)

def get_dimensions(pitch, filename=PATH+'/config/dimensions.json'):
    data = get_json(filename)
    return data[str(pitch)] 

def save_dimensions(pitch, dimensions, filename=PATH+'/config/dimensions.json'):
    data = get_json(filename)
    data[str(pitch)] = dimensions
    write_json(filename, data)


def write_json(filename=PATH+'/config/colors.json', data={}):
    _file = open(filename, 'w')
    _file.write(json.dumps(data, indent=4))
    _file.close()


