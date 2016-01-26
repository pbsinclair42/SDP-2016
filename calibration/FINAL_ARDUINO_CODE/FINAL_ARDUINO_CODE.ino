#include "SDPArduino.h"
#include "Arduino.h"
#include <Wire.h>

/***
IMPORTANT: PLEASE READ BEFORE EDITING:

  If editing file:
    1. push only working code that doesn't break it;
    2. follow the standard reasonably;
    3. read the comments before-hand.
    4. do NOT push changes if you were testing/calibrating. This
       is done in basicmotors.ino and/or other files!

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
#define POWER_RGT  99
#define POWER_BCK 99

#define KICKER_LFT_POWER 100
#define KICKER_RGT_POWER 100

// *** Globals ***

// Initial motor position for each motor.
int positions[ROTARY_COUNT] = {0};

// serial buffer and current byte
byte buffer[32];
int serial_in; // an int since Serial.read() returns an int.

int number; // James' number. TODO: Remove


// main functions: setup and loop
void setup() {

  motorAllStop(); // for sanity
  SDPsetup();

}

void loop() {
int k = 0;
  while(Serial.available() > 0 and k < 32) {
    serial_in = Serial.read();
    
    // for testing purposes
    Serial.print("Received: ");
    Serial.println((char)serial_in); 
     
    switch(serial_in){
      case 116 : // t
        fullTest();
        break;

      case 102 : // f
        forwardMotion();
        break;
      
      case 114 : // r 
        rotate();
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
     buffer[k] = byte(serial_in);
     k = k+1;
  }
  //execute_command(c);
  //getPositions();
}

void fullTest(){
  // Performs a test of all basic motions.
  // Each is executed in 5 seconds.
  // Subject to battery power, the robot should end up
  // roughly wherever it started

  testForward();
  delay(5000);
  motorAllStop();
  
  testBackward();
  delay(5000);
  motorAllStop();

  testLeft();
  delay(5000);
  motorAllStop();

  testRight();
  delay(5000);
  motorAllStop();

  testLeftForward();
  delay(5000);
  motorAllStop();

  testRightBackward();
  delay(5000);
  motorAllStop();

  testRightForward();
  delay(5000);
  motorAllStop();

  testLeftBackward();
  delay(5000);
  motorAllStop();
  
  return;
}

void forwardMotion(){
  return;
}

void rotate(){
  return;
}

void commsTest(){
  return;
}

void milestoneOne(){
  return;
}

void warning(){
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
    Serial.print (" %."); Serial.print( positions[i]);
  }
}
/*
char getChar(){
  int k=0;
  while(Serial.available() > 0) {
    serial_in_byte = byte(Serial.read());
    Serial.print("Received: ");
    Serial.print(serial_in_byte); 
    Serial.print("\r\n");
    buffer[k] = serial_in_byte;
    k = k+1;
  }
  number = ((int) (buffer[1]-'0'))*10 + ((int) (buffer[2]-'0'));
  Serial.write(buffer[1]);
  Serial.write(buffer[2]);
  Serial.write("|");
  Serial.print(number);
  Serial.write("\r\n");
  return serial_in_byte;           
}
*/

/*
void execute_command(int c){
    if (buffer[0] == 'f'){  //Works!
      Serial.write("\n yasss \n");
      Serial.write(number);
      Serial.write(buffer[2]);
      moveForward();
    }
    if (buffer[0] == 's') { //Works!
      allMotorStop() ;
    }
    if (buffer[0] == 'b'){  //Works!
      moveBackward(); 
    }
    if (buffer[0] == 'l'){
      moveLeft();
    }
    if (buffer[0] == 'r'){
      moveRight();                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
    }
    if (buffer[0] == 'e'){  //Works!
      diagonalRightForward();
    }
    if (buffer[0] == 'q'){  //works!
      diagonalLeftForward();
    }
    if (buffer[0] == 'a'){  //Works!
      rotateLeft();
    }
    if (buffer[0] == 'd'){  //Works!
      rotateRight();
    }
    if (buffer[0] == 'x'){  //Works!
      diagonalRightBackward();
    }
    if (buffer[0] == 'z'){  //works!
      diagonalLeftBackward();
    }
    //if (serial_in_byte == '5'){
    //  testUnit();
    //}
    if(buffer[0] == 'k'){
      motorKick();
    }
}
*/



void motorKick(){
  motorAllStop();
  motorBackward(KICKER_LFT, 100);
  motorBackward(KICKER_RGT, 100);                                            
  delay(500);
  motorForward(KICKER_LFT, 100);
  motorForward(KICKER_RGT, 100);
  delay(500);
  motorForward(KICKER_LFT, 0);
  motorForward(KICKER_RGT, 0); 
}

// basic test functions for sanity!

void testRightBackward() {
  motorForward(MOTOR_LFT,  POWER_LFT * 1);
  motorForward(MOTOR_RGT, POWER_RGT * 0);
  motorBackward(MOTOR_BCK, POWER_BCK * 1);
}

void testLeftBackward() {
  motorForward(MOTOR_LFT,  POWER_LFT * 0);
  motorBackward(MOTOR_RGT, POWER_RGT * 1);
  motorForward(MOTOR_BCK, POWER_BCK * 1);
}

void rotateRight() {
  motorBackward(MOTOR_LFT,  POWER_LFT * 1);
  motorBackward(MOTOR_RGT, POWER_RGT * 1);
  motorBackward(MOTOR_BCK, POWER_BCK * 1);  
}

void rotateLeft() {
  motorForward(MOTOR_LFT,  POWER_LFT * 1);
  motorForward(MOTOR_RGT, POWER_RGT * 1);
  motorForward(MOTOR_BCK, POWER_BCK * 1);  
}

void testRightForward() {
  motorBackward(MOTOR_LFT,  POWER_LFT * 1);
  motorForward(MOTOR_RGT, POWER_RGT * 0);
  motorForward(MOTOR_BCK, POWER_BCK * 1);
}

void testLeftForward() {
  motorBackward(MOTOR_LFT,  POWER_LFT * 0); 
  motorForward(MOTOR_RGT, POWER_RGT * 1);
  motorBackward(MOTOR_BCK, POWER_BCK * 1);
}

void testRight(){
  motorBackward(MOTOR_LFT,  POWER_LFT * 0.51);
  motorBackward(MOTOR_RGT, POWER_RGT * 0.51);
  motorForward(MOTOR_BCK, POWER_BCK * 0.98);
 
}

void testLeft() {
  motorForward(MOTOR_LFT,  POWER_LFT * 0.51);
  motorForward(MOTOR_RGT, POWER_RGT * 0.51);
  motorBackward(MOTOR_BCK, POWER_BCK * 0.98);
}

void testBackward(){
  motorForward(MOTOR_LFT,  POWER_LFT * 1);
  motorBackward(MOTOR_RGT, POWER_RGT *1);
  motorForward(MOTOR_BCK, POWER_BCK * 0);
}

void testForward() {
  motorBackward(MOTOR_LFT,  POWER_LFT * 1);
  motorForward(MOTOR_RGT, POWER_RGT * 1);
  motorForward(MOTOR_BCK, POWER_BCK * 0); 
}