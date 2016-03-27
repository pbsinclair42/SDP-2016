from camera import Camera
from tools import *
import cv2 
import argparse 

coordinates = []

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", help="Pitch number", required=True, choices=["0", "1"])
    return parser.parse_args()

def assign(data):
    dic = {"pitch":{"top_left": [],"top_right": [], "bottom_left" :[], "bottom_right":[]},
            "defending_left" : {"top":[], "bottom": []},
            "defending_right": {"top":[], "bottom": []},
            "goal_left": {"top":[], "bottom": []},
            "goal_right" : {"top":[], "bottom": []} }
    for x, y in data:
        if x < 100 and y < 50:
            dic["pitch"]["top_left"] = [x,y]
        elif x > 500 and y < 50:
            dic["pitch"]["top_right"] = [x,y]    
        elif x < 100 and y > 400:
            dic["pitch"]["bottom_left"] = [x,y] 
        elif x > 500 and y > 400:
            dic["pitch"]["bottom_right"] = [x,y]    
        elif 100 < x < 320 and 50 < y < 240:
            dic["defending_left"]["top"] = [x,y]       
        elif 100 < x < 320 and 240 < y < 400:
            dic["defending_left"]["bottom"] = [x,y]   
        elif 320 < x < 550 and 50 < y < 240:
            dic["defending_right"]["top"] = [x,y]       
        elif 320 < x < 550 and 240 < y < 400:
            dic["defending_right"]["bottom"] = [x,y] 
        elif x < 100 and 100 < y < 240:
            dic["goal_left"]["top"] = [x,y]
        elif x < 100 and 240 < y < 350:
            dic["goal_left"]["bottom"] = [x,y]           
        elif x > 550 and 100 < y < 240:
            dic["goal_right"]["top"] = [x,y]
        elif x > 550 and 240 < y < 350:
            dic["goal_right"]["bottom"] = [x,y]  
    return dic          

def writeCoordinates(event,x,y,flags,param):
    global img
    for center in coordinates:
        cv2.circle(img, center, 2, (0,0,0), 5)
    if event == cv2.EVENT_LBUTTONDBLCLK:
        coordinates.append((x,y))
        print (x,y)
        
def getCoordinates(pitch):
    global img
    cv2.namedWindow('Video')
    cv2.setMouseCallback('Video',writeCoordinates)
    c = Camera(pitch)
    img = step(frame, pitch)
    while(1):
        frame = c.get_frame()
        cv2.imshow('Video',img)
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break
    cv2.destroyAllWindows()        
    return coordinates        


if __name__ == "__main__":
    args = parseArgs()
    pitch = args.p
    data = getCoordinates(pitch)
    assigned  = assign(data)
    assigned
    save_dimensions(pitch, assigned)

