# Technical Specification

## Purpose

Build a robot which can play football with other similar robots.



## Naming Conventions and Terminology
Holonomic wheels : The wheels used on the robot. They have the capability to move forward and passivly move to the side.
NXT interactive servo motor: A long white motor which has lots of gears inside of it making it fairly powerful.
NXT Motor:         see above.
rotocaster:        see holonomic wheels
crossbow kicker:   this kicker has a lego piece which will pretrude and retract to hit the ball.
swing kicker:      above the height of the ball is a motor connected to a long stick. The motor turns, the stick rotates forward causing the end of it to hit 
                   the ball.



## The environment

There is a football pitch with a camera above it. This camera feeds into the laboratory next door so
it can be watched. There are 10cm high walls around the pitch and white masking tape will indicate
the pitch markings. Consiquently, robot

## The competition
Each robot must have a flat board on top of it. This board will have coloured circles on it. This is to make it possible for onlookers to tell which robot is which and to let the autonomous robots know where they and their surroundings are.



## Functional requirements
### Planning -- future
- Collect ball
- Pass
- Shoot
- Position to receive pass
- Receive pass
- Block pass
- Guard goal
- Tell teammate plans (?)
 
### Vision -- future
###### (all positions relative to the arena walls, so need to detect them too)

- Get ball position
- Detect if ball held or free (?)
- Get robot position
- Get ally position
- Get enemy positions
- Get ally rotation
- Get enemy rotation

### Sensors -- future

- Detect if currently holding ball
- Detect how far from ‘an obstacle’ such as a wall
- Detect if currently over a white line (?)

### LEGO / Communication

- Move forwards x meters
- Emergency stop
- Turn x degrees
- Grab ball
- Kick ball

The arduino receives its orders over a serial RTF connection. The RTF is set to the same frequency as the arduino board. To control the robot, send a letter and a number to the it. We have written a case statement that checks for the characters F, B, L, S, …  and methods make the robot move for however long you have specified. For example you can send "f 10" to the robot, the case statement will catch the letter f and will activate the "moveForward" method. Within this proceedure, is a while loop wich will count down from 10 while making the robot move forward. This is calibrated to make it move forward 10 centimetres. This iteration has no emergency stop capability. For the next iteration, we need to investigate interupt signals to break this while loop.

In the past, we tried using number to instruct the direction. It was intuitive if you were using the number pad on a DICE computer. The number 8 would move forward, the number 2 would move backward... and so on for each of the numberpad keys. But, we had more than 9 methods for movement. In this iteration, we could go forwards, backwards, diagonally (in four directions), left, right and rotate. So there weren't enough keys to keep to one digit direction control. We couldn't make the direction a integer as kicking, so there weren't any real advantages over using letters.

In the next iteration, we aim to make full use of the holonomic wheels. The user will send a degree and a distance to the robot. The robot will not rotate but will strafe the correct displacement.
