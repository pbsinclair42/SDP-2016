import math
def holo(angle):
    vx = math.cos(math.radians(angle))
    vy = math.sin(math.radians(angle))
    print ("Vx: ", vx)
    print ("Vy: ", vy)
    v1 = -math.sin(math.radians(30)) * vx + math.cos(math.radians(30)) * vy
    v2 = -math.sin(math.radians(150)) * vx + math.cos(math.radians(150)) * vy
    v3 = -math.sin(math.radians(270)) * vx + math.cos(math.radians(270)) * vy
    
    alpha = 0.001
    radius = 100

    scaling_factor = 1 / max(abs(v1), abs(v2), abs(v3))
    v1 *= scaling_factor
    v2 *= scaling_factor
    v3 *= scaling_factor
    
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

if __name__ == "__main__":
    angulars = []
    for i in range(0, 360, 30):
        print "HOLO", i
        angulars += [holo(i)]
    print angulars
    