#include <SDPArduino.h>

#include "SDPArduino.h"
#include "Arduino.h"
#include <Wire.h>

#define ROTARY_SLAVE_ADDRESS 5
#define ROTARY_COUNT 6
#define PRINT_DELAY 200

//encoder init
int positions[ROTARY_COUNT] = {0};
int dist = 0;

// motor encodings
int LEFT_MOTOR = 0;
int RIGHT_MOTOR = 1;
int BACK_MOTOR = 2;
int kicker = 3;

int LEFT_KICKER = 4;
int RIGHT_KICKER = 5;
// character for serial. TODO: Use a buffer for received stuff later.
char serial_in_char;

void setup()
{
   // sanity
   motorAllStop();
   SDPsetup();
   Wire.begin();
}

void loop()
{

   //kickTest()

   while(Serial.available() > 0)
   
   
   {
        serial_in_char = (char) Serial.read();
        
        // For Serial Test Purposes
        Serial.print("Received: ");
        Serial.println(serial_in_char);
        
        //forward
        if (serial_in_char == 'f'){
            motorBackward(LEFT_MOTOR,  100);
            motorForward(RIGHT_MOTOR, 95);
            motorForward(BACK_MOTOR, 0);
            updateMotorPositions();
            printMotorPositions();
            delay(500);
            updateMotorPositions();
            printMotorPositions();
        }
        //move 10cm forward
        else if(serial_in_char == '1'){
            dist=0;//reset distance travelled
            motorBackward(LEFT_MOTOR,  100);
            motorForward(RIGHT_MOTOR, 95);
            motorForward(BACK_MOTOR, 0);
            while (dist <10){
              updateMotorPositions();
              delay(500);
              updateMotorPositions();
              dist=10;
            }
        }
        //backwards
        else if (serial_in_char == 'b'){
            motorForward(LEFT_MOTOR,  100);
            motorBackward(RIGHT_MOTOR, 100);
            motorForward(BACK_MOTOR, 0);
        }
        // left
        else if (serial_in_char == 'l'){
            motorForward(LEFT_MOTOR,  50);
            motorForward(RIGHT_MOTOR, 50);
            motorBackward(BACK_MOTOR, 50);
        }
        //right
        else if (serial_in_char == 'r'){
            motorForward(LEFT_MOTOR,  100);
            motorForward(RIGHT_MOTOR, 0);
            motorForward(BACK_MOTOR, 100);
        }
        //diagonal_left
        else if (serial_in_char == 'd'){
            motorForward(LEFT_MOTOR,  0);
            motorForward(RIGHT_MOTOR, 100);
            motorBackward(BACK_MOTOR, 100);
        }
        //diagonal right
        else if (serial_in_char == 'e'){
            motorBackward(LEFT_MOTOR,  100);
            motorForward(RIGHT_MOTOR, 0);
            motorForward(BACK_MOTOR, 100);
        }
        //rotate left
        else if (serial_in_char == 'o'){
            motorForward(LEFT_MOTOR,  100);
            motorForward(RIGHT_MOTOR, 100);
            motorForward(BACK_MOTOR, 100);
        }
        //rotate right
        else if (serial_in_char == 'p'){
            motorBackward(LEFT_MOTOR,  100);
            motorBackward(RIGHT_MOTOR, 100);
            motorBackward(BACK_MOTOR, 100);
        }
        // better test for motors
        else if (serial_in_char == 't'){
          motorForward(kicker,100);
          delay(1000);
          motorBackward(kicker,20);
         delay(1000);
         motorBackward(kicker,0);
          
          //motorTest1();
        }
        //stop
        else if (serial_in_char == 's'){
            motorAllStop();
        }
   }
}

// Folks, let's keep all other functions after setup and loop

void motorTest1(){
    int i;
    for (i = 0; i < 3; i++){
        motorForward(i, 75);
    }
    // change me for calibrations and measurements
    delay(1000);
    motorAllStop();
}

void kickTest() {
   motorForward (LEFT_KICKER, 100);
   motorBackward(RIGHT_KICKER, 100);
   delay(300);
   motorBackward (LEFT_KICKER, 100);
   motorForward(RIGHT_KICKER, 100);
   delay(300);
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

  Serial.print("Motor positions: ");

  for (int i = 0; i < ROTARY_COUNT; i++) {

    Serial.print(positions[i]);

    Serial.print(' ');

  }
}
