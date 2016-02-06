#include "SDPArduino.h"
#include "Arduino.h"
#include <Wire.h>

/***
IMPORTANT: PLEASE READ BEFORE EDITING:

  If editing file:
    1. push to master only working code that doesn't break it;
    2. follow the standard reasonably;
    3. read the comments before-hand.


TODO: - Implement a function that constantly updates power to the motors during motion
      at an appropriate time-step(~50ms)
      - Split rotations at more than 180 deg to two or more steps with max deg 180

COMMS API 

1: Rotate & Move <CMD byte> <Degree to rotate> <Degree to move> <end byte>
2: Holonomic Motion <CMD byte> <Degree to rotate> <Degree to move> <end byte>
3: Kick <CMD byte> <Power/Cm> <end byte>
4: STOP <CMD byte> <end byte>
5: FLUSH Buffer
m: milestone one movement (not yet implemented)
t: sanity-test;


***/



// Rotary encoder definitions
#define ROTARY_SLAVE_ADDRESS 5
#define ROTARY_COUNT 3
#define PRINT_DELAY 200

// Motor Definitions
#define MOTOR_LFT 0
#define MOTOR_RGT 1
#define MOTOR_BCK 2

#define KICKER_LFT  5
#define KICKER_RGT  3

// Power calibrations
#define POWER_LFT  100
#define POWER_RGT  99 // was 99. 
#define POWER_BCK 95

#define KICKER_LFT_POWER 100
#define KICKER_RGT_POWER 100

// Movement Constants
#define MOTION_CONST 11.891304
#define ROTATION_CONST 4.15  // A linear function is also in effect
#define KICKER_CONST 10.0    // TODO: Calibrate

// COMMS API Byte Definitions

#define CMD_ROTMOVE B00000001
#define CMD_HOLMOVE B00000010
#define CMD_KICK    B00000100
#define CMD_STOP    B00001000
#define CMD_FLUSH   B00010000
#define CMD_DONE    B11111111
// *** Globals ***

// Initial motor position for each motor.
int positions[ROTARY_COUNT] = {0};

// serial buffer and current byte
byte byte_buffer[32];
int serial_in; // an int since Serial.read() returns an int.


// main functions: setup and loop
void setup() {

  motorAllStop(); // for sanity
  SDPsetup();
  updateMotorPositions();
  restoreMotorPositions();
  Serial.println(CMD_ROTMOVE);
  Serial.println(CMD_HOLMOVE);
  Serial.println(CMD_KICK);
  Serial.println(CMD_STOP);
  Serial.println(CMD_FLUSH);
}


void loop() {
  while(Serial.available() > 0) {
    serial_in = Serial.read();
    
    // for testing purposes
    Serial.print("Received: ");
    Serial.println((char)serial_in); 
     
    switch(serial_in){
      case 116 : // t
        fullTest();
        restoreMotorPositions();
        break;

      case 102 : // f
        forwardMotion();
        restoreMotorPositions();
        break;
      
      case 114 : // r 
        rotate();
        restoreMotorPositions();        
        break;

      case 99 :  // c
        commsTest();
        break;

      case 109 : // m
        milestoneOne();
        break;
      
      case 107 : // k
        motorKick();
        break;

      case 115 : // s
        motorAllStop();
        break;

      default:
        warning();
        break; 
     }
  }
}

void fullTest(){
  // Performs a test of all basic motions.
  // Each is executed in 5 seconds.
  // Subject to battery power, the robot should end up
  // roughly wherever it started

  testForward();
  delay(3000);
  motorAllStop();
  
  testBackward();
  delay(3000);
  motorAllStop();

  testLeft();
  delay(3000);
  motorAllStop();

  testRight();
  delay(3000);
  motorAllStop();

  testLeftForward();
  delay(3000);
  motorAllStop();

  testRightBackward();
  delay(3000);
  motorAllStop();

  testRightForward();
  delay(3000);
  motorAllStop();

  testLeftBackward();
  delay(3000);
  motorAllStop();
  
  return;
}

void forwardMotion(){
  int buff_index = 0;
  int forward = 1;
  char char_byte;
  int parse_val = 1;
  int rotary_val = 0;
  
  // Buffer all numbers
  delay(10); // ask Nantas about this bug. Make sure it doesn't fuck up RF comms
  while(Serial.available() > 0){
    delay(10); // Why does this happen ?!
    byte_buffer[buff_index++] = byte(Serial.read());
  }
  
  // Parse value
  while (buff_index-- > 0){
    char_byte = (char) byte_buffer[buff_index];
    if (char_byte == '-')
      forward = -1;
    else if (char_byte >= '0' && char_byte <= '9'){
      rotary_val += ((int) char_byte - '0') * parse_val;
      parse_val *= 10;
    }
  }
  // Debugs for rotary value
  //Serial.print("Forward Value: ");
  //Serial.println(rotary_val);
  //Serial.flush(); // waits for serial printing to finish! TODO:Remove
  
  rotary_val = (int) (MOTION_CONST * rotary_val);
  
  // Move forward/backward
  if (forward > 0)
    testForward();
  else
    testBackward();
  
  while (-1 * forward *  positions[MOTOR_LFT] < rotary_val && forward * positions[MOTOR_RGT] < rotary_val){
    updateMotorPositions();
  }
  motorAllStop();
  
  return;
}

void rotate(){
  int buff_index = 0;
  int left = 1;
  char char_byte;
  int parse_val = 1;
  int rotary_val = 0;
  int bias;
  
  // Buffer all numbers
  delay(10); // ask mentor(s) about this bug. Make sure it doesn't fuck up RF comms due to difference in bandwidth :?
  while(Serial.available() > 0){
    delay(10); // Why does this happen ?!
    byte_buffer[buff_index++] = byte(Serial.read());
  }
  
  // Parse value
  while (buff_index-- > 0){
    char_byte = (char) byte_buffer[buff_index];
    if (char_byte == '-')
      left = -1;
    else if (char_byte >= '0' && char_byte <= '9'){
      rotary_val += ((int) char_byte - '0') * parse_val;
      parse_val *= 10;
    }
  }
  // Debugs for rotary value
  //Serial.print("Rotary Value: ");
  //Serial.println(rotary_val);

  // Linear function to correct all motion less than 180 deg
  rotary_val = (int) ((1 / 120.0) * rotary_val * rotary_val + 3 * rotary_val);

  // bias fix due to rotary encoder initial positions
  updateMotorPositions();
  bias = positions[0] + positions[1] + positions[2];
  
  // move forward/backward
  if (left > 0)
    rotateLeft();
  else
    rotateRight();
  
  while (left *  (positions[MOTOR_LFT] + positions[MOTOR_RGT] + positions[MOTOR_BCK]) < rotary_val + left * bias){
    updateMotorPositions();
  }
  motorAllStop();
  
  return;
}

void commsTest(){
  while (true){
    if (Serial.available() > 0){
      Wire.beginTransmission(69);
      byte x = Serial.read(); // well, that was interesting -_-
      //Serial.println(x);
      Wire.write(x);
      Wire.endTransmission();  
    } 
  }
}

void milestoneOne(){
  return;
}

void warning(){
  Serial.println("Warning: Unrecognized command");
  return;
}

void updateMotorPositions() {

  // Request motor position deltas from rotary slave board
  Wire.requestFrom(ROTARY_SLAVE_ADDRESS, ROTARY_COUNT);

  // Update the recorded motor positions
  for (int i = 0; i < ROTARY_COUNT; i++) {
    positions[i] += (int8_t) Wire.read();  // Must cast to signed 8-bit type
  }
}


void printMotorPositions() {
  Serial.println("Motor positions (Left, Right, back): ");
  delay(PRINT_DELAY);  // Delay to avoid flooding serial out
  
  for (int i = 0; i < ROTARY_COUNT; i++) {
    Serial.print( positions[i]); Serial.print (" "); 
  }
}

void restoreMotorPositions(){
  int i;
  for (i = 0; i < ROTARY_COUNT; i++){
    positions[i] = 0;
  }
  return;
}

void motorKick(){
  int buff_index = 0;
  int left = 1;
  char char_byte;
  int parse_val = 1;
  int rotary_val = 0;
  int bias;
  
  motorAllStop();
  while(Serial.available() > 0){
    delay(10); // Why does this happen ?!
    byte_buffer[buff_index++] = byte(Serial.read());
  }
  
  // Parse value
  while (buff_index-- > 0){
    char_byte = (char) byte_buffer[buff_index];
    if (char_byte == '-')
      left = -1;
    else if (char_byte >= '0' && char_byte <= '9'){
      rotary_val += ((int) char_byte - '0') * parse_val;
      parse_val *= 10;
    }
  }
  
  delay(100);
  Serial.print(rotary_val);
  motorBackward(KICKER_LFT, rotary_val);
  motorBackward(KICKER_RGT, rotary_val);                                            
  delay(500);
  motorForward(KICKER_LFT, KICKER_LFT_POWER);
  motorForward(KICKER_RGT, KICKER_RGT_POWER);
  delay(500);
  motorAllStop();
}

// basic test functions for sanity!

void testRightBackward() {
  motorForward(MOTOR_LFT, POWER_LFT * 1);
  motorForward(MOTOR_RGT, POWER_RGT * 0);
  motorBackward(MOTOR_BCK, POWER_BCK * 1);
}

void testLeftBackward() {
  motorForward(MOTOR_LFT, POWER_LFT * 0);
  motorBackward(MOTOR_RGT, POWER_RGT * 1);
  motorForward(MOTOR_BCK, POWER_BCK * 1);
}

void rotateRight() {
  motorBackward(MOTOR_LFT, POWER_LFT * 1);
  motorBackward(MOTOR_RGT, POWER_RGT * 1);
  motorBackward(MOTOR_BCK, POWER_BCK * 1);  
}

void rotateLeft() {
  motorForward(MOTOR_LFT, POWER_LFT * 1);
  motorForward(MOTOR_RGT, POWER_RGT * 1);
  motorForward(MOTOR_BCK, POWER_BCK * 1);  
}

void testRightForward() {
  motorBackward(MOTOR_LFT, POWER_LFT * 1);
  motorForward(MOTOR_RGT, POWER_RGT * 0);
  motorForward(MOTOR_BCK, POWER_BCK * 1);
}

void testLeftForward() {
  motorBackward(MOTOR_LFT, POWER_LFT * 0); 
  motorForward(MOTOR_RGT, POWER_RGT * 1);
  motorBackward(MOTOR_BCK, POWER_BCK * 1);
}

void testRight(){
  motorBackward(MOTOR_LFT, POWER_LFT * 0.51);
  motorBackward(MOTOR_RGT, POWER_RGT * 0.51);
  motorForward(MOTOR_BCK, POWER_BCK * 0.98);
 
}

void testLeft() {
  motorForward(MOTOR_LFT, POWER_LFT * 0.51);
  motorForward(MOTOR_RGT, POWER_RGT * 0.51);
  motorBackward(MOTOR_BCK, POWER_BCK * 0.98);
}

void testBackward(){
  motorForward(MOTOR_LFT, POWER_LFT * 1);
  motorBackward(MOTOR_RGT, POWER_RGT * 1);
  motorForward(MOTOR_BCK, POWER_BCK * 0);
}

void testForward() {
  motorBackward(MOTOR_LFT, POWER_LFT * 1);
  motorForward(MOTOR_RGT, POWER_RGT * 1);
  motorForward(MOTOR_BCK, POWER_BCK * 0); 
}