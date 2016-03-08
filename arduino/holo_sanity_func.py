import math
def holo(angle):
    vx = math.cos(math.radians(angle))
    vy = math.sin(math.radians(angle))
    print ("Vx: ", vx)
    print ("Vy: ", vy)
    v1 = -math.sin(math.radians(30)) * vx + math.cos(math.radians(30)) * vy
    v2 = -math.sin(math.radians(150)) * vx + math.cos(math.radians(150)) * vy
    v3 = -math.sin(math.radians(270)) * vx + math.cos(math.radians(270)) * vy
    
    scaling_factor = 1 / max(abs(v1), abs(v2), abs(v3))
    v1 *= scaling_factor
    v2 *= scaling_factor
    v3 *= scaling_factor

    for i in [v1, v2, v3]:
        if abs(i) < 0.01:
            print 0, 
        else:
            print i, 
