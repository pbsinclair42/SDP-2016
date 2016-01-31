# User Guide

## 1. How to Run

### Setting up before a match

//TODO

### Running the software

//TODO


## 2. Hardware

// TODO add images

### On the Robot

- Three holonomic (omnidirectional) wheels, each powered by a single ungeared NXT motor
- A simple kicker powered by two PF Medium motors
- An arduino board connected to an 8xAA battery pack, a power board and a rotary encoder board

### Off the robot

- USB to mini USB cable (used to upload programs to the Arduino)
- RF stick (used to make the computer talk to the robot)
- Battery charger (charges batteries)
- Battery tester (tests batteries)
- A ball (Hint: get this in the opponent's goal)

## 3. Software

### Overview

//TODO

### Installing the requirements

//TODO

## Troubleshooting
### The robot won't move
#### Check that the RF stick and the arduino RF chip are on the same frequency.
Connect the arduino in the robot, and the RF stick to the computer.
In the terminal type "screen /dev/ttyACM0 115200" if your USB stick is in the top left port and
"screen /dev/ttyACM1 115200" if its in the right port. Next type "+++", if you don't see the word "OK"
then type "~~~". The terminal will not print out what you have typed once screen has started.
After every command press enter, and then ctrl+a k to clear the output. You should expect it to say
OK after each command. These commands will reset your RF stick to their factory settings.
ATRE
ATAC
ATWR
ATDN

To get back into command mode, press +++ this time and continue entering commands as before.

ATID0004
ATAC
ATRP1
ATAC

In the terminal type "screen /dev/ttyACM0 115200" if your USB stick is in the top left port and
"screen /dev/ttyACM1 115200" if its in the right port.

Next type "+++", if you don't see the word "OK"
then type "~~~".

SRF stick to factory settings:

ATRE

ATAC

ATWR

ATDN

Now enter command mode again - it will be +++ this time:

ATID00XX (where XX is your group number)

ATAC

ATRP1

ATAC

ATCNXX (where XX is the hexidecimal number for your group's frequency)

ATAC

ATWR

ATDN

Now exit screen (ctrl-a k) and reset your Arduino radio device to factory

default:

$ screen /dev/ttyACMX 115200 (where X is the port number for you Ardunio USB

                              connection)

Enter command mode (+++ or ~~~) and execute the following commands:

ATRE

ATAC

ATWR

ATDN

Enter command mode (now +++) and execute the following commands:

ATID00XX (where XX is your group number)

ATAC

ATRP1

ATAC

ATCNXX (where XX is the hexidecimal number for your group's frequency)

ATAC

ATBD 1C200 <--- This step is only for the Arduino, not the stick.

ATAC

ATWR

ATDN

Here is an Arduino script to test this has worked:

#include <Wire.h>

#include <SDPArduino.h>

void setup() {

  SDPsetup();

  serial_test();

}

void serial_test() {

  helloWorld();

  while (!Serial.find("TEST"));

  Serial.println("Message received!");

}

Program your Arduino, and disconnect it.

Then open a screen for you SRF stick port.

Press the reset button on your Ardunio.

You should see "hello world" on the screen for you SRF stick port.

Type in TEST into the screen (you won't be able to see this).

You should see "Message received!".
