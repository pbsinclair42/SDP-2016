def angle_diff(start, end):
    phi = abs(end - start) % 360
    if phi > 180:
        return 360 - phi
    else:
        return phi