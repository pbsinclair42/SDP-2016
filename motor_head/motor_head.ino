#include <SDPArduino.h>


/*

 * Master board sample code to be used in conjuction with the rotary encoder

 * slave board and sample code.

 * This sketch will keep track of the rotary encoder positions relative to

 * the origin. The origin is set to the position held when the master board

 * is powered.

 *

 * Rotary encoder positions are printed to serial every 200ms where the

 * first result is that of the encoder attached to the port at 11 o'clock

 * on the slave board (with the I2C ports at at 12 o'clock). The following

 * results are in counter-clockwise sequence.

 *

 * Author: Chris Seaton, SDP Group 7 2015

 */

 

#include <Wire.h>



#define ROTARY_SLAVE_ADDRESS 5

#define ROTARY_COUNT 6

#define PRINT_DELAY 200


int LEFT_MOTOR = 0;
int RIGHT_MOTOR = 1;
int BACK_MOTOR = 2;

int LEFT_KICKER = 4;
int RIGHT_KICKER = 5;

int LeftPower = 100;
int RightPower = 99;
int BackPower = 99;

// Initial motor position is 0.

int positions[ROTARY_COUNT] = {0};

int serial_in_char;

void setup() {

  digitalWrite(8, HIGH);  // Radio on

  Serial.begin(115200);  // Serial at given baudrate

  Wire.begin();  // Master of the I2C bus
  
  // Krassy: all motors forward to be able to test things!
  
  
  //moveForward();
  
 // motorForward(0, 100);
  //motorForward(1, 100);
 // motorForward(2, 98);
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

  Serial.print("Motor positions (Left, Right, back): ");

  for (int i = 0; i < ROTARY_COUNT; i++) {

    Serial.print(positions[i]);

    Serial.print(' ');

  }

  Serial.println();

  Serial.println( positions[0] + positions[1]);

  delay(PRINT_DELAY);  // Delay to avoid flooding serial out

}




void loop() {
  
  int c = getChar();
  direct(c);
  getPositions();
}

int getChar(){
    while(Serial.available() > 0) {
       serial_in_char = (int) Serial.read();
       serial_in_char -= 48;
       Serial.print("Received: ");
       Serial.println(serial_in_char); 
    }
   return serial_in_char;           
}

void direct(int c){

    if (serial_in_char == 8){  //Works!
       moveForward();
    }
    if (serial_in_char == 0) { //Works!
      allMotorStop() ;
    }
    if (serial_in_char == 2){  //Works!
       moveBackward(); 
    }
    if (serial_in_char == 4){
       moveLeft();
    }
    if (serial_in_char == 6){
       moveRight();                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
    }
    if (serial_in_char == 9){  //Works!
        diagonalRightForward();
    }
    
    if (serial_in_char == 7){  //works!
      diagonalLeftForward();
    }
    if (serial_in_char == 10){  //Works!
       rotateLeft();
    }
    if (serial_in_char == 11){  //Works!
       rotateRight();
    }
    
    if (serial_in_char == 3){  //Works!
        diagonalRightBackward();
    }
    if (serial_in_char == 1){  //works!
      diagonalLeftBackward();
    }
    if (serial_in_char == 5){
      testUnit();
    }
}

void diagonalRightBackward() {
 motorForward(LEFT_MOTOR,  LeftPower*1);
 motorForward(RIGHT_MOTOR, RightPower*0);
 motorBackward(BACK_MOTOR, BackPower*1);
}

void diagonalLeftBackward() {
 motorForward(LEFT_MOTOR,  LeftPower*0);
 motorBackward(RIGHT_MOTOR, RightPower*1);
 motorForward(BACK_MOTOR, BackPower*1);
}

void rotateRight() {
 motorBackward(LEFT_MOTOR,  LeftPower*1);
 motorBackward(RIGHT_MOTOR, RightPower*1);
 motorBackward(BACK_MOTOR, BackPower*1);  
}


void rotateLeft() {
 motorForward(LEFT_MOTOR,  LeftPower*1);
 motorForward(RIGHT_MOTOR, RightPower*1);
 motorForward(BACK_MOTOR, BackPower*1);  
}

void diagonalRightForward() {
 motorBackward(LEFT_MOTOR,  LeftPower*1);
 motorForward(RIGHT_MOTOR, RightPower*0);
 motorForward(BACK_MOTOR, BackPower*1);
}

void diagonalLeftForward() {
 motorBackward(LEFT_MOTOR,  LeftPower*0); 
 motorForward(RIGHT_MOTOR, RightPower*1);
 motorBackward(BACK_MOTOR, BackPower*1);
}

void moveRight(){
/*
  motorBackward(LEFT_MOTOR,  LeftPower *0.71);
 motorBackward(RIGHT_MOTOR, RightPower * 0.35);
 motorForward(BACK_MOTOR, BackPower *0.85); 
  
  
 motorForward(LEFT_MOTOR,  LeftPower *1);
 motorBackward(RIGHT_MOTOR, RightPower * 1);
 motorForward(BACK_MOTOR, BackPower *1);
 */
  motorBackward(LEFT_MOTOR,  LeftPower *0.51);
 motorBackward(RIGHT_MOTOR, RightPower * 0.51);
 motorForward(BACK_MOTOR, BackPower * 0.98);
 
}

void moveLeft() {
  /*
 motorForward(LEFT_MOTOR,  LeftPower *0.35);
 motorForward(RIGHT_MOTOR, RightPower * 0.71);
 motorBackward(BACK_MOTOR, BackPower *0.85); 
 */
  motorForward(LEFT_MOTOR,  LeftPower *0.51);
 motorForward(RIGHT_MOTOR, RightPower * 0.51);
 motorBackward(BACK_MOTOR, BackPower * 0.98);
 

 
}

void moveBackward(){
  motorForward(LEFT_MOTOR,  100);
  motorBackward(RIGHT_MOTOR, 100);
  motorForward(BACK_MOTOR, 0);
}
void moveForward() {
  motorBackward(LEFT_MOTOR,  LeftPower * 1);
  motorForward(RIGHT_MOTOR, RightPower * 1);
  motorForward(BACK_MOTOR, BackPower *0); 
}
 
void testUnit(){
  motorForward(LEFT_MOTOR,  100);
  motorForward(RIGHT_MOTOR, 99);
  motorForward(BACK_MOTOR, 99);   
}  

void allMotorStop() {
  motorForward(LEFT_MOTOR,  LeftPower * 0);
  motorForward(RIGHT_MOTOR, RightPower * 0);
  motorForward(BACK_MOTOR, BackPower * 0); 
}

void getPositions(){
    updateMotorPositions();
    printMotorPositions();
}
