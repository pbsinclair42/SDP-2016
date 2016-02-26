# Technical Specification

## Purpose

Build a robot which can play football with other similar robots.



## Naming Conventions and Terminology

## Facts and Assumptions

## The environment

There is a football pitch with a camera above it. This camera feeds into the laboratory next door so it can be watched. There are 10cm high walls around the pitch and white masking tape will indicate the pitch markings.

## The competition
Each robot must have a flat board on top of it. This board will have coloured circles on it. This is to make it possible for on lookers to tell which robot is which and to let the autonomous robots know where they and their surroundings are.



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
- Detect how far from ‘an obstacle’
- Detect if currently over a white line (?)

### LEGO / Communication

- Move forwards x meters
- Emergency stop
- Turn x degrees
- Grab ball
- Kick ball

The arduino receives its orders over a serial RTF connection.. The RTF is set to the same frequency as the arduino board. A single character is send via this connection. We have written a case statement that checks for the characters F, B, L, S, …  which make the robot move in a certain way.

## Scope and boundaries 

## Game rules
to be released
