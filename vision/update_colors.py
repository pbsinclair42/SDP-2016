import cv2
from tools import *

sliders = {'H low':['min',0,180],
            'H high':['max',0,180],
            'S low':['min',1,255],
            'V low':['min',2,255]}

redSliders = {'red' :{'H low red ':['min',0,180],
                    'H high red':['max',0,180],
                    'S low red':['min',1,255],
                    'V low red':['min',2,255]
                    },
                'maroon' : {
                    'H low  maroon':['min',0,180],
                    'H high maroon':['max',0,180],
                    'S low maroon':['min',1,255],
                    'V low maroon':['min',2,255]
                }
            }      

def nothing(x):
    pass                

def denoiseMask(mask):
    kernel =  cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    po = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    po = cv2.morphologyEx(po, cv2.MORPH_OPEN, kernel)
    return po

def initTrackbars(color):
    colors = get_colors()
    cv2.namedWindow(color)

    if color is 'red':
        for name in redSliders['red']:
            num = redSliders['red'][name][1]
            cv2.createTrackbar(name,color,int(colors[color][redSliders['red'][name][0]][num]),redSliders['red'][name][2],nothing)
        
        for name in redSliders['maroon']:
            num = redSliders['maroon'][name][1]
            cv2.createTrackbar(name,color,int(colors['maroon'][redSliders['maroon'][name][0]][num]),redSliders['maroon'][name][2],nothing)
   
    else:
        for name in sliders:
            num = sliders[name][1]
            cv2.createTrackbar(name,color,int(colors[color][sliders[name][0]][num]),sliders[name][2],nothing)

def recordValues(color, frame):

    colors = {}
    blur = cv2.GaussianBlur(frame,(11,11), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    if color is 'red':
        h_low_red = cv2.getTrackbarPos('H low red',color)
        h_high_red = cv2.getTrackbarPos('H high red',color)
        s_low_red = cv2.getTrackbarPos('S low red',color)
        v_low_red = cv2.getTrackbarPos('V low red',color)

        h_low_maroon = cv2.getTrackbarPos('H low maroon',color)
        h_high_maroon = cv2.getTrackbarPos('H high maroon',color)
        s_low_maroon = cv2.getTrackbarPos('S low maroon',color)
        v_low_maroon = cv2.getTrackbarPos('V low maroon',color)

        red_mask = cv2.inRange(hsv, (h_low_red, s_low_red, v_low_red), (h_high_red, 255, 255))
        maroon_mask = cv2.inRange(hsv, (h_low_maroon, s_low_maroon, v_low_maroon), (h_high_maroon, 255, 255))
        mask = cv2.bitwise_or(red_mask, maroon_mask)
        cv2.imshow(color, denoiseMask(mask)) 
        # assign new values
        colors['red'] = {'min': np.array([h_low_red, s_low_red, v_low_red]), 'max': np.array([h_high_red, 255, 255]) }
        colors['maroon'] = {'min': np.array([h_low_maroon, s_low_maroon, v_low_maroon]),'max': np.array([h_high_maroon, 255, 255]) } 
    
    else:
        h_low = cv2.getTrackbarPos('H low',color)
        h_high = cv2.getTrackbarPos('H high',color)
        s_low = cv2.getTrackbarPos('S low',color)
        v_low = cv2.getTrackbarPos('V low',color)

        mask = cv2.inRange(hsv, (h_low, s_low, v_low), (h_high, 255, 255))
        cv2.imshow(color, denoiseMask(mask)) 
        # assign new values
        colors[color] = {'min': np.array([h_low, s_low, v_low]),'max': np.array([h_high, 255, 255])}

    # write fixed values into 'json' file
    return colors       

def closeMask(color, values):
    save_colors(values)   
    cv2.destroyWindow(color)    


