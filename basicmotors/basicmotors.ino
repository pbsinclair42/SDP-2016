#include <SDPArduino.h>

#include "SDPArduino.h"
#include "Arduino.h"
#include <Wire.h>

// motor encodings
int LEFT_MOTOR = 0;
int RIGHT_MOTOR = 1;
int BACK_MOTOR = 2;

// character for serial. TODO: Use a buffer for received stuff later.
char serial_in_char;

void setup()
{
   // sanity
   motorAllStop();
   SDPsetup();
}

void loop()
{
   while(Serial.available() > 0)
   {
        serial_in_char = (char) Serial.read();
        
        // For Serial Test Purposes
        Serial.print("Received: ");
        Serial.println(serial_in_char);
        
        //forward
        if (serial_in_char == 'f'){
            motorBackward(LEFT_MOTOR,  100);
            motorForward(RIGHT_MOTOR, 100);
            motorForward(BACK_MOTOR, 0);
        }
        //backwards
        else if (serial_in_char == 'b'){
            motorBackward(LEFT_MOTOR,  100);
            motorBackward(RIGHT_MOTOR, 100);
            motorForward(BACK_MOTOR, 0);
        }
        // left
        else if (serial_in_char == 'l'){
            motorForward(LEFT_MOTOR,  0);
            motorForward(RIGHT_MOTOR, 100);
            motorForward(BACK_MOTOR, 100);
        }
        //right
        else if (serial_in_char == 'r'){
            motorForward(LEFT_MOTOR,  100);
            motorForward(RIGHT_MOTOR, 0);
            motorForward(BACK_MOTOR, 100);
        }
        //diagonal_left
        else if (serial_in_char == 'd'){
            motorForward(LEFT_MOTOR,  100);
            motorForward(RIGHT_MOTOR, 100);
            motorForward(BACK_MOTOR, 100);
        }
        //diagonal right
        else if (serial_in_char == 'e'){
            motorForward(LEFT_MOTOR,  100);
            motorForward(RIGHT_MOTOR, 100);
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
            motorForward(LEFT_MOTOR,  100);
            motorForward(RIGHT_MOTOR, 100);
            motorForward(BACK_MOTOR, 100);
        }
        // better test for motors
        else if (serial_in_char == 't'){
            motorTest1();
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
