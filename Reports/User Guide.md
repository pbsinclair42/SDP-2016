# User Guide

## 1. How to Run

### Setting up before a match

To load the arduino code onto the arduino therough the proveded micro-USB cable launch the arduino IDE through the terminal and upload "FINAL_ARDUINO_CODE.INO" to the arduino.
This file can be found in /calibration/FINAL_ARDUINO_CODE.
Before you test the comms system please remember to plug in the arduino battetries.

To set up the RF comms system, plug in the Rf stick into your machine - check it is using serial port ttyACM0 which can be found in /dev/.
Load up jerial.py, which is found in /comms/ - This is a serial writer to the arduino, test everything works by trying some commands e.g. f10, r-90
Now that we know the system is operational you can either send instructions through jseral.py or if you have any prewritten command-chains then you can use those simply by launching that python program. 

###Robot Commands

For use in jserial of if you are writing your own command-chains, the commands look like this:
* f DISTANCE - Forwards/backwards with DISTANCE being the number of cm you wish to move, this supports negative numbers
* r DEGREES - rotationwhere DEGREES is the number of degrees you wish to rotate, this supports negative numbers, where positive denotes c counter-clockwise direction
* k POWER - kicker launch with set power (up to 100)
* s - stop all motors
To view example of command-chaining look at some of the files in /comms/ such as ForwardFifty.py

## 2. Hardware

### On the Robot
- 3 holonomic wheels: connected to the external of the frame with rotational symetry
- 8xAA battery pack: lie at the bottom of the robot, at the centre of the frame, to keep the centre of gravity low and steady. The batteries need to be changed fairly often,  simply remove the arduino from the top of the frame and lift the battery pack out.
- 3 NXT interactive servo motors: to turn the wheels
- Rotary encoder board: To track the positions of the motors
- Motor control board: to instruct the motors.
- Arduino xino: communicate with the rotary encoder board and the motor controler board, it receives and processes commands.


### Off the robot

- USB to mini USB cable (used to upload programs to the Arduino)
- RF stick (used to make the computer talk to the robot)
- Battery charger (charges batteries)
- Battery tester (tests batteries)
- A ball 

## 3. Software

### Overview

The software consists of a sketch for the arduino microcontroller, a communication system, a planning/strategy system and a vision system, all of which are currently still in development. The arduino IDE makes uploading and verifying arduino code a piece of cake. For communication we also make use of python and librarys serial and time. All of these can be downloaded or found on DICE.

### Installing the requirements
#### Arduino IDE
This is open source and can simply be downloaded from the arduino website.  It should already be installed on DICE, open the terminal and type "arduino" and the software will likely open.

#### python 2.7
This downloadable from the python website. It should already be installed on DICE, open the terminal and type "python" and the interpreter will open. But you aren't finished yet, python doesn't include 'pyserial' by default, so run:
    Pip install --user pyserial




## Troubleshooting
### The robot won't move
#### Check the batteries aren't dead.
Move the arduino and cabels out of your way and disconnect the battery pack from the arduino board. Pull the batteries out of the robot frame and swap each battery with a new/charged one. 
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

Next type "+++", if you don't see the word "OK", then type "~~~".

SRF stick to factory settings:

ATRE
ATAC
ATWR
ATDN

Now enter command mode again - it will be +++ this time:

ATID0004
ATAC
ATRP1
ATAC
ATCN27 
ATAC
ATWR
ATDN

Now exit screen (use ctrl-a k) and reset your Arduino radio device to factory

default:

"screen /dev/ttyACM0 115200" if your Ardunio USB connection is in the top left port and "screen /dev/ttyACM1 115200" if its in the right port.

Enter command mode (+++ or ~~~) and execute the following commands:

ATRE
ATAC
ATWR
ATDN

Enter command mode (now +++) and execute the following commands:

ATID0004
ATAC
ATRP1
ATAC
ATCN27
ATAC
ATBD 1C200
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