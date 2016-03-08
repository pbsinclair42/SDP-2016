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

if __name__ == "__main__":
    angles(30, 90)
    angles(60, 180)
    angles(70, 300)
    angles(150, 30)
    angles(300, 60)
    angles(330, 120)
