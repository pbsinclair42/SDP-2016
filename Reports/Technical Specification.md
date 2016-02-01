# Technical Specification

## Purpose

Build a robot which can play football with other similar robots.



## Naming Conventions and Terminology
Holonomic wheels : The wheels used on the robot. They have the capability to move forward and passivly move to the side.
NXT interactive servo motor: A long white motor which has lots of gears inside of it making it fairly powerful.
NXT Motor:         see above.
rotocaster:        see holonomic wheels
crossbow kicker:   a method of kicking the ball in a straight line. It involves a 



## The environment

There is a football pitch with a camera above it. This camera feeds into the laboratory next door so
it can be watched. There are 10cm high walls around the pitch and white masking tape will indicate
the pitch markings. Consiquently, robot

## The competition
Each robot must have a flat board on top of it. This board will have coloured circles on it. This is to make it possible for onlookers to tell which robot is which and to let the autonomous robots know where they and their surroundings are.



## Functional requirements
### Planning
- Collect ball
- Pass
- Shoot
- Position to receive pass
- Receive pass
- Block pass
- Guard goal
- Tell teammate plans (?)

### Vision
###### (all positions relative to the arena walls, so need to detect them too)

- Get ball position
- Detect if ball held or free (?)
- Get robot position
- Get ally position
- Get enemy positions
- Get ally rotation
- Get enemy rotation

### Sensors

- Detect if currently holding ball
- Detect how far from ‘an obstacle’ such as a wall
- Detect if currently over a white line (?)

### LEGO / Communication

- Move forwards x meters
- Emergency stop
- Turn x degrees
- Grab ball
- Kick ball

The arduino receives its orders over a serial RTF connection. The RTF is set to the same frequency as the arduino board. A single character is send via this connection. We have written a case statement that checks for the characters F, B, L, S, …  which make the robot move in a certain way.

## Scope and boundaries
### Scope

### Boundaries
The robot will be controlled without using a GUI.

## Game rules
to be released
