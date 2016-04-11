from tracker import *
from camera import Camera
from algebra import *
from update_colors import *

import argparse
import time
import zmq


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t",
                        help="Our Team Colour",
                        required=True,
                        choices=["yellow", "bright_blue"])
    parser.add_argument("-m",
                        help = "My Robot Colour",
                        required=True,
                        choices = ['green', 'pink'])
    parser.add_argument("-b",
                        help="Ball Colour",
                        required=True,
                        choices=["red", "blue"])
    parser.add_argument("-p",
                        help="Pitch number 0=3.D04/1=3.D03",
                        required=True,
                        choices=["0","1"])
    parser.add_argument("-test",
                        help = "Are you using live video feed?",
                        required=False,
                        choices = ['0', '1'])

    return parser.parse_args()

'''
    Main function that gets current data about objects on the pitch and sends it to
    planner/world.py file. This function also draws object identifications on the shown
    video feed as well as alows to adjust color value thresholds.
'''
def main():
    # socket setup for threading
    ctx = zmq.Context()
    socket = ctx.socket(zmq.PUB)
    socket.bind("tcp://*:5555")

    # get command line arguments
    args = parse_args()
    testing = 0
    if (args.test is not None):
        testing = int(args.test)
    our_team_color = args.t
    ball_color = args.b
    my_color = args.m

    # initialize camera object
    c = Camera(int(args.p), 0, testing)

    # create our robot as object:
    robot_tracker = RobotTracker(our_team_color, my_color, 10)
    ball_tracker = BallTracker(ball_color)

    # convert string colors into GBR
    colors = {}
    colors['red'] = (0, 0, 255)
    colors['blue'] = (255, 0, 0)

    keys = {'b':'blue',
            'c':'bright_blue',
            'g':'green',
            'p':'pink',
            'r':'red',
            'y':'yellow'}

    previously_pressed = ''
    # get color thresholds from 'json' file
    data = get_colors()

    # main feed controller:
    print "Sending data..."
    while True:
        frame = c.get_frame()
        # get pressed key value
        k = cv2.waitKey(5) & 0xFF
        if ((previously_pressed == chr(k) or k == 27) and not not previously_pressed):
            closeMask(keys[previously_pressed], data)
            previously_pressed = ''

        elif not previously_pressed and chr(k) in keys:
            previously_pressed = chr(k)
            initTrackbars(keys[chr(k)])

        elif not not previously_pressed:
            new_data = recordValues(keys[previously_pressed], frame)
            for col in new_data:
                data[col] = new_data[col]
        # if Esc was pressed, quit top window
        elif k == 27:
            break

        # get robot orientations and centers, also get ball coordinates
        robots_all = None
        ball_centre = None
        try:
            ball_center = ball_tracker.getBallCoordinates(frame)
            robots_all = robot_tracker.getRobotParameters(frame)
        except ValueError:
            print("Exception calculating ball")
            raise

        if ball_center is not None:
            _ball = ball_center
            cv2.circle(frame, (int(_ball[0]), int(_ball[1])), 7,
                       colors[ball_color], 2)
            cv2.putText(frame, 'BALL',
                        (int(_ball[0]) - 15, int(_ball[1]) + 15),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5,
                        colors[ball_color])


        for (side, color) in robot_tracker.identifierCombinations():
            center = robots_all[(side, color)]['center']
            orientation = robots_all[(side, color)]['orientation']
            if (center is not None):
                cv2.circle(frame,
                        (int(center[0]),
                            int(center[1])), 20, (0,0,255), 2)
                cv2.putText(frame, side, (int(center[0]) - 15,
                                        int(center[1]) + 30),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,255))
                cv2.putText(frame, color, (int(center[0]) - 20,
                                                int(center[1]) + 40),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,255))

            if (orientation is not None):
                v, a = orientation
                x, y = center
                if v is not None:
                    draw_vector = (x + v[0], y + v[1])
                else:
                    draw_vector = (0, 0)

                cv2.line(frame,
                        (int(center[0]), int(center[1])),
                        (int(draw_vector[0]), int(draw_vector[1])), (0, 0, 255), 2)

        # tmp = {}        
        tmp = robots_all.copy()
        tmp.update({"ball_center": ball_center})
        socket.send_pyobj(tmp)
        # show current frame 
        cv2.imshow('frame', frame)

    print "Stopping data sender."
    c.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
