#include "B4SDP.h"
#include "Arduino.h"
#include <Wire.h>

/***
IMPORTANT: PLEASE READ BEFORE EDITING:

    If editing file:
        1. push to master only working code that doesn't break it;
        2. follow the standard reasonably;
        3. read the comments before-hand.


TODO: 
    - Split rotations at more than 180 deg to two or more steps with max deg 180

COMMS API 

1: Rotate & Move <CMD byte> <Degree to rotate> <Degree to move> <end byte>
2: Holonomic Motion <CMD byte> <Degree to rotate> <Degree to move> <end byte>
3: Kick <CMD byte> <Power/Cm> <end byte> <end byte>
4: STOP <CMD byte> <end byte> <end byte> <end byte>
5: FLUSH Buffer <CMD byte> <end byte> <end byte> <end byte>
6. 
t: sanity-test;


***/

// Motor Definitions
#define MOTOR_LFT 0
#define MOTOR_RGT 1
#define MOTOR_BCK 2
#define KICKER_LFT 3
#define KICKER_RGT 4
#define GRABBER 4
#define KICKER 5 // TODO: Remove once second kicker motor has been added

// Power calibrations
#define POWER_LFT    255
#define POWER_RGT    252  
#define POWER_BCK 242
#define KICKER_PWR 255
#define KICKER_LFT_POWER 255
#define KICKER_RGT_POWER 255
#define GRABBER_POWER 255

// Movement Constants
#define MOTION_CONST 11.891304
#define ROTATION_CONST 4.15    // A linear function is also in effect
#define KICKER_CONST 10.0        // TODO: Calibrate

// COMMS API Byte Definitions
#define CMD_ROTMOVE B00000001 // Buffered: MSB 1 performs CCW rotation
#define CMD_HOLMOVE B00000010 // Buffered: NOT YET IMPLEMENTED
#define CMD_KICK    B00000100 // Buffered
#define CMD_STOP    B00001000 // Buffered
#define CMD_GRAB    B00010000 // Buffered
#define CMD_UNGRAB  B00100000 // Buffered
#define CMD_FLUSH   B01000000 // Immediate. Flushes the buffer and awaits new commands
#define CMD_END     B11111111 // Buffered

#define CMD_ERROR   B11111111 // Sent for errors
#define CMD_FULL    B11111110 // Sent if buffer is full
#define CMD_RESEND  B11111100 // if all commands haven't been received in 500 miliseconds
#define CMD_ACK     B11111000 // Sent after command has been received

// utils
#define BUFFERSIZE 256
#define ROTARY_COUNT 3
#define IDLE_STATE 0

// *** Globals ***

// A finite state machine is required to provide concurrency between loop and 
// serialEvent functions which both support reading serial while moving and
// rotary-encoder-based motion
byte MasterState = 0; 

// positions of wheels based on rotary encoder values
int positions[ROTARY_COUNT] = {0};

// circular command buffer
byte command_buffer[BUFFERSIZE];
byte buffer_index = 0; // current circular buffer utilization index
byte command_index = 0; // current circular buffer command index
unsigned long serial_time; // used for the millis function.
unsigned long rot_move_time;
// rotation parameters
byte rotMoveMode = 0;
int rotaryTarget;
int rotaryBias;



int rotary_target;
int motion_target;
int holono_target;


// Main Functions: Setup, Loop and SerialEvent
void setup() {
    SDPsetup();
    motorAllStop(); // for sanity
    Serial.println("What the fuck is going on?");
    Serial.print(CMD_END);
    Serial.print(CMD_GRAB);
    // to get rid of potential bias
    updateMotorPositions(positions);
    restoreMotorPositions(positions);
}

void loop() {
  //Serial.print(MasterState);
  int state_end = 0;
  if (MasterState != 0){
     Serial.println(MasterState); 
  }
    switch(MasterState){
        case IDLE_STATE:
            if (command_index != buffer_index && command_index + 4 <= buffer_index){
                Serial.println("I AM CHANGING STATE MOTHAFUCkaaaah");
                Serial.print("CMD: ");
                Serial.println(command_index);
                Serial.print("BUF");
                Serial.println(buffer_index);
                MasterState = command_buffer[command_index];
                restoreMotorPositions(positions);
                delay(1000);  
          }
            break;
        case CMD_ROTMOVE:
            state_end = rotMoveStep();
            break;
        case CMD_HOLMOVE:
            state_end = holoMoveStep();
            break;
        case CMD_KICK:
            state_end = kickStep();
            break;
        case CMD_GRAB:
            Serial.println("I should be grabbing!");
            state_end = grabStep();
            break;
        case CMD_UNGRAB:
            state_end = unGrabStep();
            break;
        case CMD_STOP:
            state_end = 1;
            motorAllStop();
            break;
        case CMD_FLUSH:
            state_end = 0;
            buffer_index = 0;
            command_index = 0;
            MasterState = IDLE_STATE;
            break;
        default:
            Serial.print("VERY BAD ERROR");
            Serial.print(MasterState);
            Serial.println(CMD_ERROR);
            MasterState = IDLE_STATE;
            state_end = 1;
            break;
        }
        if (state_end){
            Serial.println("Blaaaaaaaaaaaaaaaah");
            MasterState = IDLE_STATE;
            command_index += 4;
        }
    }

/* 
SerialEvent occurs whenever a new data comes in the
hardware serial RX. This routine is run between each
time loop() runs.
*/

void serialEvent() {
    serial_time = millis();
    while (Serial.available()) {
        command_buffer[buffer_index++] = Serial.read();
        Serial.println(command_buffer[buffer_index - 1]);
        Serial.println(buffer_index);
        Serial.println("-------------");
        if (buffer_index % 4 == 0){
            // acknowledge proper command
            if (command_buffer[buffer_index - 1] == CMD_END){
                Serial.print(CMD_ACK);
                Serial.print(command_buffer[buffer_index - 4]);
                Serial.print(command_buffer[buffer_index - 3]);
                Serial.print(command_buffer[buffer_index - 2]);
                Serial.print(command_buffer[buffer_index - 1]);
            }
            // report bad command
            else{
                Serial.println("SANITY CHECK");
                Serial.print(CMD_ERROR);
                Serial.print(command_buffer[buffer_index - 1]);
                buffer_index = buffer_index - 4;
            }
            
            if (command_buffer[buffer_index - 4] == CMD_FLUSH){
                buffer_index = 0;
                command_index = 0;
                motorAllStop();
            }
        } else if (millis() - serial_time > 500){
            Serial.print(CMD_RESEND);
            while(buffer_index %4 != 0) {
                buffer_index--;
            }
        }
    }
}

int rotMoveStep(){
    byte left, degrees, centimeters;
    switch(rotMoveMode){

        // calculate rotation target and start rotating
        case 0 :
            degrees = command_buffer[command_index + 1];
            left = (MasterState >> 7); // left becomes MSB of master state/current command
            left = left == 0 ? 1 : -1;
            
            if (!degrees){
                rotMoveMode = 2;
                return 0;
            }

            if (degrees <= 180) 
                rotaryTarget = (int) ((1 / 120.0) * degrees * degrees + 3 * degrees);
            else
                rotaryTarget == ROTATION_CONST;

            updateMotorPositions(positions);
            rotaryBias = positions[0] + positions[1] + positions[2];

            if (left == 1)
                rotateLeft();
            else
                rotateRight();

            rotMoveMode = 1;
            return 0;
        
        // chck whether to stop during rotation;
        case 1 :
            left = MasterState >> 7; // left becomes MSB of master state/current command
            left = left == 0 ? 1 : -1;

            if (left * (positions[MOTOR_LFT] + positions[MOTOR_RGT] + positions[MOTOR_BCK]) < rotaryTarget + left * rotaryBias){
                updateMotorPositions(positions);
            }
            else{
                motorAllStop();
                restoreMotorPositions(positions);
                rotMoveMode = 2;
            }
            return 0;
        
        // calculate movement target and start moving forward
        case 2 :
            centimeters = command_buffer[command_index + 2];
            
            if (!centimeters){
                rotMoveMode = 0;
                return 1;
            }

            rotaryTarget = (int) (MOTION_CONST * centimeters);
            testForward();

            rotMoveMode = 3;
            return 0;

        // perform movement
        case 3 :
            if (-1 * positions[MOTOR_LFT] < rotaryTarget && positions[MOTOR_RGT] < rotaryTarget){
                updateMotorPositions(positions);
                return 0;
            }
            else{
                motorAllStop();
                restoreMotorPositions(positions);
                rotMoveMode = 0;
                return 1;
            }
        default:
            return -1;
            break;       
    }
}
int holoMoveStep(){
    Serial.print(CMD_ERROR);
    Serial.println("Holonomic motion not yet implemented");
    return 1;
}

int kickStep(){
    byte kick_val = command_buffer[command_index + 1];
    motorBackward(GRABBER, kick_val); 
    delay(100);
    Serial.print(kick_val);
    motorForward(KICKER, kick_val);                                        
    delay(500);
    motorBackward(KICKER, KICKER_LFT_POWER);
    delay(400);
    motorBackward(KICKER, 0);
    motorForward(GRABBER, kick_val);
    delay(500); 
    motorAllStop();
    return 1;
}

int grabStep(){
    // TODO: Parallelize
    motorAllStop();
    motorBackward(GRABBER,255);
    delay(500);
    motorBackward(GRABBER, 0);
    return 1;
}

int unGrabStep(){
  // TODO: Parallelize
  motorForward(GRABBER,100);
  delay(500);
  motorBackward(GRABBER,0);
  return 1;
}

int motorKick(){
    int buff_index = 0;
    int left = 1;
    char char_byte;
    int parse_val = 1;
    int rotary_val = 0;
    int bias;
    
    motorAllStop();
    while(Serial.available() > 0){
        delay(10); // Why does this happen ?!
        command_buffer[buff_index++] = byte(Serial.read());
    }
    
    // Parse value
    while (buff_index-- > 0){
        char_byte = (char) command_buffer[buff_index];
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
    return 1;
}

// basic test functions for sanity!
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

