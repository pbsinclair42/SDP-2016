import pygame
from simulator import *
from robotAI import *
from moveables import Robot


## Requires pygame 
## Extend moveable.Robot to include a picture of the toplate, draw and update methods.
## Use the simulator.tick method to make things happen.

# our supreme robot
simulatedMe = RobotImage(name="simulatedMe")
# Team 3's robot
simulatedAlly = RobotImage(name="simulatedAlly")
# the two robots we're against
simulatedEnemies = [RobotImage(name="simulatedPinkEnemy"), RobotImage(name="simulatedGreenEnemy")]
# a list containing all robots on the field for convenience
simulatedRobots = [simulatedMe, simulatedAlly]+simulatedEnemies
# guess what this could possibly be
simulatedBall = Ball(name="simulatedBall")


pygame.init()

gray = (128,128,128)
blue = (0,255,0)
green = (0,0,255)

box  = pygame.display.set_mode((600, 400),0,32)
cmd = pygame.Surface((600, 300))
pitch = pygame.Surface((600, 100))

def refresh():
    box.fill(green)
    cmd.fill(blue)
    pitch.fill(gray)
# set the font to use.   
font = pygame.font.Font('freesansbold.ttf', 22)

class RobotImage(Robot):
    def rot_center(image, angle):
        """rotate an image while keeping its center and size"""
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

    def __init__(self):
        self.bot = pygame.sprite.Sprite()
        self.bot.image = pygame.image.load("me.png")
        self.origional = self.bot.image
        super().__init__()
        simulator.kick(self, 100)
   
   
    def drawRobot(self,box):
        box.blit(self.bot.image, [self.x, self.y])
        return box

    def update(self):
        self.currentActionQueue.append({'action': simulator.SimulatorActions.ungrab, 'timeLeft': simulator.UNGRAB_TIME})
        super().tick()
        self.x, self.y = simulator.simulatedMe.currentPoint.x,  simulator.simulatedMe.currentPoint.y 
        self.rotation = simulator.simulatedMe.currentRotation
        self.bot.image = robot.rot_center(self.origional,  self.rotation)



quit = False

while not (quit):
    
    
    refresh()
    simulatedMe.update()
    pitch = simulatedMe.drawRobot(pitch)
    box.blit(pitch, (600, 300)) # box: green, pitch: gray, cmd:blue
    box.blit(cmd,   [0, 100])
    pygame.display.flip()
    pygame.time.wait (100)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit = True
            pygame.display.quit()
	     
