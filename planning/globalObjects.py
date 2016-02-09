from moveables import Robot, Ball

# our supreme robot
me = Robot(name="me")
# Team 3's robot
ally = Robot(name="ally")
# the two robots we're against
enemies = [Robot(name="pinkEnemy"), Robot(name="greenEnemy")]
# a list containing all robots on the field for convenience
robots = [me, ally]+enemies
# guess what this could possibly be
ball = Ball(name="ball")
