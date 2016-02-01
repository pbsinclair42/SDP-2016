from helperClasses import Point, BallStatus

# Note that the vision system should pick one of the enemy robots to be enemy A and one to be enemy B, and keep that consistent throughout.
# It doesn't matter which is which, so long as it stays the same

def getBallCoords():
    """Returns the position of the ball relative to the pitch"""
    # TODO: replace stub with info from vision system
    return Point(15,20)

def getBallStatus():
    """Returns which robot, if any, is holding the ball"""
    # TODO: replace stub with info from vision system
    return BallStatus.free

def getMyCoords():
    """Returns the position of our robot relative to the pitch"""
    # TODO: replace stub with info from vision system
    return Point(40,35)

def getAllyCoords():
    """Returns the position of our teammate relative to the pitch"""
    # TODO: replace stub with info from vision system
    return Point(100,155)

def getEnemyCoords():
    """Returns the positions of the two enemy robots relative to the pitch"""
    # TODO: replace stub with info from vision system
    return [Point(80,10), Point(220,76)]

def getMyRotation():
    """Returns the rotation of our robot in radians between -pi and pi"""
    # TODO: replace stub with info from vision system
    return 1.2

def getAllyRotation():
    """Returns the rotation of our teammate in radians between -pi and pi"""
    # TODO: replace stub with info from vision system
    return 1.63

def getEnemyRotation():
    """Returns the rotation of the two enemy robots in radians between -pi and pi"""
    # TODO: replace stub with info from vision system
    return [2.1, -0.67]

def getAllRobotCoords():
    """Returns an array of the position of all the robots"""
    return [getMyCoords(), getAllyCoords()]+getEnemyCoords()

def getAllRobotRotations():
    """Returns an array of the rotation of all the robots"""
    return [getMyRotation(), getAllyRotation()]+getEnemyRotation()

def getAllRobotDetails():
    """Returns an array of tuples of the position and rotation of all the robots"""
    return zip(getAllRobotCoords(), getAllRobotRotations())