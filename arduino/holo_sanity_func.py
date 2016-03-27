import math
import random
def holo(angle):
    vx = math.cos(math.radians(angle))
    vy = math.sin(math.radians(angle))
    print ("Vx: ", vx)
    print ("Vy: ", vy)
    v1 = -math.sin(math.radians(30)) * vx + math.cos(math.radians(30)) * vy  + 0.5
    v2 = -math.sin(math.radians(150)) * vx + math.cos(math.radians(150)) * vy + 0.5
    v3 = -math.sin(math.radians(270)) * vx + math.cos(math.radians(270)) * vy + 0.5
    
    alpha = 0.001
    radius = 100

   # scaling_factor = 1 / max(abs(v1), abs(v2), abs(v3))
   # v1 *= scaling_factor
   # v2 *= scaling_factor
   # v3 *= scaling_factor
    
    motor_list = [v1, v2, v3]
    for idx, i in enumerate(motor_list):
        if abs(i) < 0.0001:
            print 0, 
        else:
            print i,
            motor_list[idx] = 0


    accel_x = -math.sin(math.radians(30)) * v1 - math.sin(math.radians(150)) * v2 - math.sin(math.radians(270)) * v3
    accel_y = math.cos(math.radians(30)) * v1 + math.cos(math.radians(150)) * v2 + math.cos(math.radians(270)) * v3
    accel_angular = (1.0 / alpha) * v1 + (1.0 / alpha) * v2 + (1.0 / alpha) * v3
    if abs(accel_x) < 0.0001:
        accel_x = 0
    if abs(accel_y) < 0.0001:
        accel_y = 0
    if abs(accel_angular) < 0.0001:
        accel_angular = 0

    print
    print "Accel in X", accel_x
    print "Accel in Y", accel_y
    print "angular accel", accel_angular

    return accel_angular

def angle_diff(start, end):
    phi = abs(end - start) % 360
    if phi > 180:
        return 360 - phi
    else:
        return phi


def angles(a1, a2):
    print "A1 is:", a1,
    print "A2 is:", a2,
    d = abs(a1 - a2) % 360
    print "Diff is:", 360 - d if d > 180 else d
    print "Right: ", 360 - d if a1 < a2 else d
    print "Left: ", d if a1 < a2 else 360 - d
    print

def magnetic_to_holonomic(angle_to_face, angle_to_move):
    #heading = random.choice(range(0, 360))
    heading = 266
    print "Heading", heading
    ref_point = heading - 90
    print "Ref point", ref_point
    angle = angle_to_move - ref_point
    print "Angle Clean", angle
    if angle < 0:
        angle = 360 + angle

    if angle > 360:
        angle = 360 - angle
    print "Angle", angle 
    return angle
if __name__ == "__main__":
    #test = True
    #for i in range(0, 360):
    #    for j in range(0, 10000):
    #        a = magnetic_to_holonomic(200, 200)
    #        test = True and a >= 0 and a <= 360
    #print test
    magnetic_to_holonomic(215, 215)