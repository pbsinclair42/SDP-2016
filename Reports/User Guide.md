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

### Seperate

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

### Check that the RF stick and the arduino RF chip are on the same frequency.
In the terminal type "screen /dev/ttyACM0 115200" if your USB stick is in the top left port and "screen /dev/ttyACM1 115200" if its in the right port. Next type "+++" 
ATRE
ATAC
ATWR
ATDN




SRF Stick Setup Information

===========================

Note this guide is not complete, and may contain unnecessary steps, but this

worked for my group, and should work no matter the initial configuration of your

SRF stick / Arduino.

Plug the SRF stick into a USB port on your dice machine.

Connect your Arduino to the computer via the microUSB wire.

The top USB ports are identified as follows:

Top left: ttyACM0

Top right: ttyACM1

Run the following on terminal:

$ screen /dev/ttyACMX 115200 (where X is the port number for your SRF stick)

Enter command mode by typing either +++ or ~~~ (do not press enter).

Once you are in command mode you should see OK.

Note that you automatically exit command mode after 5 seconds of no commands.

Also, the default settings for screen mean you cannot see what you type.

For this to work, I think you have to do it in one session, so if you run out

of time, start again (the ATAC command confirms settings and ATWR command writes

settings).

Press enter after each command and press ctrl-a shift-c to clear the output

after every command, so you can confirm that a command has worked by receiving

OK (if you receive ERR, you have entered the command incorrectly, if you

do not receive OK, you have exited command mode).

After getting into command mode, execute the following commands to reset the

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
