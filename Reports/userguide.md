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

//TODO generate lego style instructions using LDD


A kicker is mounted on the front of the robot - use this as a point of reference for calibration if required.

## 3. Software

### Overview

//TODO

### Installing the requirements

To use the comms system the pyserial library has to be installed on your machine. Use the command "pip install --user pyserial" to accomplish this.
There are no other necicery requirments for the comms system or the arduino itself.

##Vision System
//TODO

## Troubleshooting

//TODO
