#include "SDPArduino.h"
#include "Arduino.h"
#include <Wire.h>

/***
IMPORTANT: PLEASE READ BEFORE EDITING:

  If editing file:
    1. push only working code that doesn't break it;
    2. follow the standard reasonably;
    3. read the comments before-hand.
    4. 

***/


// Rotary encoder definitions
#define ROTARY_SLAVE_ADDRESS 5
#define ROTARY_COUNT 6
#define PRINT_DELAY 200

// Motor Definitions
#define MOTOR_LFT 0
#define MOTOR_RGT 1
#define MOTOR_BCK 2

#define KICKER_LFT  5
#define KICKER_RGT  3

#define POWER_LFT  100
#define POWER_RGT  99
#define POWER_BCK 99

#define KICKER_LFT_POWER 100
#define KICKER_RGT_POWER 100

// Initial motor position is 0 for each motor.
int positions[ROTARY_COUNT] = {0};

char buffer[4];
int number;
char serial_in_char;

void setup() {
  SDPsetup();
  digitalWrite(8, HIGH);  // Radio on

  Serial.begin(115200);  // Serial at given baudrate

  Wire.begin(); 

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




void loop() {
  char c = getChar();
  direct(c);
  getPositions();
}

char getChar(){
  int k=0;
  while(Serial.available() > 0) {
    serial_in_char = (char)Serial.read();
    Serial.print("Received: ");
    Serial.print(serial_in_char); 
    Serial.print("\r\n");
    buffer[k] = serial_in_char;
    k = k+1;
  }
  number = ((int) (buffer[1]-'0'))*10 + ((int) (buffer[2]-'0'));
  Serial.write(buffer[1]);
  Serial.write(buffer[2]);
  Serial.write("|");
  Serial.print(number);
  Serial.write("\r\n");
  return serial_in_char;           
}

void direct(int c){
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
    if (serial_in_char == '5'){
      testUnit();
    }
    if(buffer[0] == 'k'){
      motorKick();
    }
}

void motorKick(){
  motorBackward(KICKER_LFT, 100);
  motorBackward(KICKER_RGT, 100);                                            
  delay(500);
  motorForward(KICKER_LFT, 100);
  motorForward(KICKER_RGT, 100);
  delay(500);
  motorForward(KICKER_LFT, 0);
  motorForward(KICKER_RGT, 0); 
}

void diagonalRightBackward() {
  motorForward(MOTOR_LFT,  POWER_LFT * 1);
  motorForward(MOTOR_RGT, POWER_RGT * 0);
  motorBackward(MOTOR_BCK, POWER_BCK * 1);
}

void diagonalLeftBackward() {
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

void diagonalRightForward() {
  motorBackward(MOTOR_LFT,  POWER_LFT * 1);
  motorForward(MOTOR_RGT, POWER_RGT * 0);
  motorForward(MOTOR_BCK, POWER_BCK * 1);
}

void diagonalLeftForward() {
  motorBackward(MOTOR_LFT,  POWER_LFT * 0); 
  motorForward(MOTOR_RGT, POWER_RGT * 1);
  motorBackward(MOTOR_BCK, POWER_BCK * 1);
}

void moveRight(){
  motorBackward(MOTOR_LFT,  POWER_LFT * 0.51);
  motorBackward(MOTOR_RGT, POWER_RGT * 0.51);
  motorForward(MOTOR_BCK, POWER_BCK * 0.98);
 
}

void moveLeft() {
  motorForward(MOTOR_LFT,  POWER_LFT * 0.51);
  motorForward(MOTOR_RGT, POWER_RGT * 0.51);
  motorBackward(MOTOR_BCK, POWER_BCK * 0.98);
}

void moveBackward(){
  motorForward(MOTOR_LFT,  POWER_LFT * 1);
  motorBackward(MOTOR_RGT, POWER_RGT *1);
  motorForward(MOTOR_BCK, POWER_BCK * 0);
}

void moveForward() {
  motorBackward(MOTOR_LFT,  POWER_LFT * 1);
  motorForward(MOTOR_RGT, POWER_RGT * 1);
  motorForward(MOTOR_BCK, POWER_BCK * 0); 
}
 
void testUnit(){
  motorForward(MOTOR_LFT,  100);
  motorForward(MOTOR_RGT, 99);
  motorForward(MOTOR_BCK, 99);   
}  

void allMotorStop() {
  motorForward(MOTOR_LFT,  POWER_LFT * 0);
  motorForward(MOTOR_RGT, POWER_RGT * 0);
  motorForward(MOTOR_BCK, POWER_BCK * 0); 
}

void getPositions(){
  updateMotorPositions();
  printMotorPositions();
}
