#include <SDPArduino.h>
#include <SDPArduino.h>
#include "SDPArduino.h"
#include "Arduino.h"
#include <Wire.h>


// TODO: use #define for those
int MOTOR_LEFT = 0;
int MOTOR_LEFT_MAX = 100;  //  TODO: calibrate
int MOTOR_RIGHT = 1;
int MOTOR_RIGHT_MAX = 100; // TODO: calibrate
int MOTOR_BACK = 2; 
int MOTOR_BACK_MAX = 100; // TODO: calibrate
int KICKER_1 = 3;
int KICKER_2 = 4;

int serial_index;
byte serial_in;
byte serial_end = byte('\n'); // to be agreed upon

byte serial_buffer[63];

void setup()
{
   // sanity
   motorAllStop();

   // compulsory for normal operation
   SDPsetup();
}

void loop(){

	while(Serial.available() > 0){
		serial_in = Serial.read();
		if (serial_in == serial_end){
			execute_command(serial_buffer);
			serial_index = 0;
			}
		else{
			serial_buffer[serial_index] = serial_in;
			++serial_index;
		}

	}

}

void execute_command(byte serial_buffer[]){
	/*(switch(serial_buffer){
		case(...) : call_function_command();
		break
		case(...) : call_function_command();
		break
		...
		...
		...
		default : unrecognized command!
	}
	*/
	return 0;
}

void full_rotation_test(){
	motorForkard(MOTOR_LEFT, MOTOR_LEFT_MAX / 2);
	motorForward(MOTOR_RIGHT, MOTOR_RIGHT_MAX / 2);
	motorForward(MOTOR_BACK, MOTOR_BACK_MAX / 2);
	delay(5000);
	
	motorBackward(MOTOR_LEFT, MOTOR_LEFT_MAX / 2);
	motorBackward(MOTOR_RIGHT, MOTOR_RIGHT_MAX / 2);
	motorBackward(MOTOR_BACK, MOTOR_BACK_MAX / 2);
	delay(5000);
	
	motorAllStop();
	return 0;
}

void full_front_back_test(){
	motorBackward(MOTOR_LEFT, MOTOR_LEFT_MAX);
	motorForward(MOTOR_RIGHT, MOTOR_RIGHT_MAX);
	motorForward(MOTOR_BACK, 0);
	delay(5000);

	motorBackward(MOTOR_LEFT, MOTOR_LEFT_MAX);
	motorForward(MOTOR_RIGHT, MOTOR_RIGHT_MAX);
	motorBackward(MOTOR_BACK, 0);
	delay(5000);
	
	motorAllStop();
	return 0;
}

void full_diagonal_test(){
	motorBackward(MOTOR_LEFT, MOTOR_LEFT_MAX);
	motorForward(MOTOR_RIGHT, 0);
	motorForward(MOTOR_BACK, MOTOR_BACK_MAX);
	delay(5000);

	motorBackward(MOTOR_LEFT, 0);
	motorForward(MOTOR_RIGHT, MOTOR_RIGHT_MAX);
	motorBackward(MOTOR_BACK, MOTOR_BACK_MAX);
	delay(5000);
	
	motorAllStop();
	return 0;
}

void full_strafe_test(){
	motorForward(MOTOR_LEFT, MOTOR_LEFT_MAX / 2);
	motorForward(MOTOR_RIGHT, 0);
	motorBackward(MOTOR_BACK, MOTOR_BACK_MAX);
	delay(5000);

	motorBackward(MOTOR_LEFT, 0);
	motorBackward(MOTOR_RIGHT, MOTOR_RIGHT_MAX);
	motorBackward(MOTOR_BACK, MOTOR_BACK_MAX);
	delay(5000);

	motorAllStop();
	return 0;
}

// TODO: Rework for calibration
/*
void updateMotorPositions() {

  // Request motor position deltas from rotary slave board

  Wire.requestFrom(ROTARY_SLAVE_ADDRESS, ROTARY_COUNT);

  

  // Update the recorded motor positions

  for (int i = 0; i < ROTARY_COUNT; i++) {

    positions[i] += (int8_t) Wire.read();  // Must cast to signed 8-bit type

  }
  */
