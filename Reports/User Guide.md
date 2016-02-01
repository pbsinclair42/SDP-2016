# User Guide

## 1. How to Run

### Setting up before a match

To load the arduino code onto the arduino therough the proveded micro-USB cable launch the arduino IDE through the terminal and upload "FINAL_ARDUINO_CODE.INO" to the arduino.
This file can be found in /calibration/FINAL_ARDUINO_CODE.
Before you test the comms system please remember to plug in the arduino battetries.

To set up the RF comms system, plug in the Rf stick into your machine - check it is using serial port ttyACM0 which can be found in /dev/.
Load up jerial.py, which is found in /comms/ - This is a serial writer to the arduino, test everything works by trying some commands e.g. f10, r-90
Now that we know the system is operational you can either send instructions through jseral.py or if you have any prewritten command-chains then you can use those simply my launching that python program. 

###Robot Commands
For use in jserial of if you are writing your own command-chains, the commands look like this:
* f DISTANCE - Forwards/backwards with DISTANCE being the number of cm you wish to move, this supports negative numbers
* r DEGREES - rotationwhere DEGREES is the number of degrees you wish to rotate, this supports negative numbers
* k POWER - kicker launch with set power (up to 100)
* s - stop all motors
To view example of command-chaining look at some of the files in /comms/ such as ForwardFifty.py



## 2. Hardware

// TODO add images

### On the Robot

The robot consists of a lego frame with 3 NXT rotocaster wheels each with an NXT interactive servo motor.
Contained within the frame is a cage for the batteries and the arduino xino.
Mounted on the exerior of the robot is the rotary encoder board and Motor control board.
* To swap out the battery pack, simply remove the arduino from the top of the frame and lift the battery pack out.


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
