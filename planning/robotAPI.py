
def turn(x):
    """Rotates the robot x radians clockwise.  Use negative numbers to rotate anticlockwise.  """
    # TODO: Replace stub with actual code to communicate with robot
    print("Turning "+abs(x)+"radians "+"clockwise" if x>=0 else "anticlockwise")


def move(distance, angle):
    """Moves `distance` cm at a direction of `angle` radians"""
    # TODO: Replace stub with actual code to communicate with robot
    print("Moving "+distance+"cm at an angle of "+x+" radians")


def kick(distance):
    """Kicks the ball `distance` cm"""
    # TODO: Replace stub with actual code to communicate with robot
    print("Kicking ball "+distance+"cm")


def grab():
    """Attempts to grab the ball"""
    # TODO: Replace stub with actual code to communicate with robot
    print("Grabbing ball")


def stop():
    """Stops all motors"""
    # TODO: Replace stub with actual code to communicate with robot
    print("Stopping all motors")
