#include "B4SDP.h"
#include "Arduino.h"
#include <Math.h>
#include <Wire.h>

/***
IMPORTANT: PLEASE READ BEFORE EDITING:

    If editing file:
        1. push to master only working code that doesn't break it;
        2. follow the standard reasonably;
        3. read the comments before-hand.

***/

// Motor Definitions
#define MOTOR_LFT   0
#define MOTOR_RGT   1
#define MOTOR_BCK   2
#define GRABBER     4
#define KICKER      5 // TODO: Remove once second kicker motor has been added

// Power calibrations
#define POWER_LFT 255
#define POWER_RGT 252  
#define POWER_BCK 242
#define KICKER_PWR 255
#define KICKER_LFT_POWER 255
#define KICKER_RGT_POWER 255
#define GRABBER_POWER 255

// temporal calibrations
#define KICK_TIME 550
#define GRAB_TIME 650

// Movement Constants
#define MOTION_CONST 11.891304
#define ROTATION_CONST 0.4
#define KICKER_CONST 10.0  

// COMMS API Byte Definitions
#define CMD_ROTMOVE    B00000001 // Buffered: MSB 1 performs CCW rotation
#define CMD_ROTMOVECCW B10000001 // Buffered: MSB 1 performs CCW rotation
#define CMD_HOLMOVE    B00000010 // Buffered: NOT YET IMPLEMENTED
#define CMD_KICK       B00000100 // Buffered
#define CMD_STOP       B00001000 // Buffered
#define CMD_GRAB       B00010000 // Buffered
#define CMD_UNGRAB     B00100000 // Buffered
#define CMD_FLUSH      B01000000 // Immediate. Flushes the buffer and awaits new commands
#define CMD_END        B11111111 // Buffered

#define CMD_DONE       B01101111 // Sent when command is finished

#define CMD_ERROR      B11111111 // Sent for errors
#define CMD_FULL       B11111110 // Sent if buffer is full
#define CMD_RESEND     B11111100 // if all commands haven't been received in 500 miliseconds
#define CMD_ACK        B11111000 // Sent after command has been received

// utils
#define BUFFERSIZE 256
#define ROTARY_COUNT 3
#define IDLE_STATE 0

// *** Globals ***

// A finite state machine is required to provide concurrency between loop and 
// serialEvent functions which both support reading serial while moving and
// rotary-encoder-based motion
byte MasterState = 0; 
byte finishGrabbing = 0;
// positions of wheels based on rotary encoder values
int positions[ROTARY_COUNT] = {0};

// circular command buffer
byte command_buffer[BUFFERSIZE];
byte buffer_index = 0; // current circular buffer utilization index
byte command_index = 0; // current circular buffer command index

unsigned long serial_time; // used for the millis function.
unsigned long command_time;

// rotation parameters
byte rotMoveGrabMode = 0;
int rotaryTarget;
int rotaryBias;

// circular buffer counters
byte bufferOverflow = 0;
byte commandOverflow = 0;

int rotary_target;
int motion_target;
int holono_target;


// Main Functions: Setup, Loop and SerialEvent
void setup() {
    SDPsetup();
    motorAllStop(); // for sanity
    // to get rid of potential bias
    updateMotorPositions(positions);
    restoreMotorPositions(positions);
    MasterState = 0;
    finishGrabbing = 0;
    buffer_index = 0;
    command_index = 0;
    rotMoveGrabMode = 0;
    bufferOverflow = 0;
    commandOverflow = 0;
    /* Custom commands can be initialized below */
    
    //command_buffer[0] = 2;
    //command_buffer[1] = 45;
    //command_buffer[2] = 45;
    //command_buffer[3] = 255;
    //buffer_index = 4;
    //Serial.println("Begin");
  }

void loop() {
  int state_end = 0;
  
  // Switch statement for the FSM state
  switch(MasterState){
        case IDLE_STATE:
            if ((command_index != buffer_index && command_index + 4 <= buffer_index && commandOverflow == bufferOverflow) || 
                 commandOverflow < bufferOverflow){
                MasterState = command_buffer[command_index];
                restoreMotorPositions(positions);
          }
            break;
        case CMD_ROTMOVE:
            state_end = rotMoveStep();
            break;
        case CMD_ROTMOVECCW:
            state_end = rotMoveStep();
            break;
        case CMD_HOLMOVE:
            state_end = holoMoveStep();
            break;
        case CMD_KICK:
            state_end = kickStep();
            break;
        case CMD_GRAB:
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
            Serial.println(CMD_ERROR);
            MasterState = IDLE_STATE;
            state_end = 1;
            break;
        }
    if (state_end){
        MasterState = IDLE_STATE;
        command_index += 4;
        
        // check for circular buffer end
        if (command_index == 0){
            commandOverflow++;
        }
        Serial.print(CMD_DONE);
        
        
        }
    }

/* 
SerialEvent occurs whenever a new data comes in the
hardware serial RX. This routine is run between each
time loop() runs.
*/

void serialEvent() {
    int target_value; // for targetting buffer checks so as not to do buffer[0 - 1]
    serial_time = millis();
    while (Serial.available()) {
        // note overflow to maintain circular buffer
        if (buffer_index == 255){
            bufferOverflow++;
        }
        // read command
        command_buffer[buffer_index++] = Serial.read();
        
        if (buffer_index % 4 == 0){
            // acknowledge proper command
            if (buffer_index == 0){
                target_value = 256;
            } else {
                target_value = buffer_index;
            }
         
            if (command_buffer[target_value - 1] == CMD_END){
                Serial.print(CMD_ACK);
                Serial.print("-");
                Serial.print(command_buffer[target_value - 4]);
                Serial.print("-");
                Serial.print(command_buffer[target_value - 3]);
                Serial.print("-");
                Serial.print(command_buffer[target_value - 2]);
                Serial.print("-");
                Serial.print(command_buffer[target_value - 1]);
                
            }
            // report bad command
            else{
                Serial.print("Bad Command");
                Serial.print(CMD_ERROR);
                buffer_index = target_value - 4;
            }
            
            if (command_buffer[target_value - 4] == CMD_FLUSH){
                restoreState();
            } else if (command_buffer[target_value - 4] == CMD_STOP){
                motorAllStop();
                rotMoveGrabMode = 0;
                MasterState = 0;
                bufferOverflow = 0;
                commandOverflow = 0;
            }


        } else if (millis() - serial_time > 500){ // TODO: Break this only here;
            Serial.print("Time-Out");
            Serial.println(CMD_ERROR);
            while(buffer_index %4 != 0) {
                buffer_index--;
            }
        }
    }
}

void restoreState(){
    buffer_index = 0;
    command_index = 0;
    bufferOverflow = 0;
    commandOverflow = 0;
    rotMoveGrabMode = 0;
    MasterState = 0;
    motorAllStop();
}


int rotMoveStep(){
    // values for target calculation
    int left;
    byte degrees, centimeters;


    switch(rotMoveGrabMode){

        // calculate rotation target and start rotating
        case 0 :
            degrees = command_buffer[command_index + 1];
            left = (MasterState >> 7); // left becomes MSB of master state/current command
            left = left == 0 ? 1 : -1;
            
            if (!degrees){
                rotMoveGrabMode = 2;
                return 0;
            }
            
            // calculate target based on piece-wise linear approximation for
            // know values of 30, 45, 60, 90, 120, 180 degrees
            rotaryTarget = (int) (calculateRotaryTarget(degrees) * degrees);  
            
            // restore and update motor positions to account for initial bias
            // based on wheels & rotary encoders;
            restoreMotorPositions(positions);
            updateMotorPositions(positions);
            rotaryBias = positions[0] + positions[1] + positions[2];

            if (left == 1)
                rotateLeft();
            else
                rotateRight();
            
            rotMoveGrabMode = 1;
            return 0;
        
        // chck whether to stop during rotation;
        case 1 :
            left = MasterState >> 7; // left becomes MSB of master state/current command
            left = left == 0 ? 1 : -1;
            if (left * (positions[MOTOR_LFT] + positions[MOTOR_RGT] + positions[MOTOR_BCK]) < rotaryTarget + left * rotaryBias){
                updateMotorPositions(positions);
                rotMoveGrabMode = 1;
            }
            else{
                // delay to make sure motor actions are not being performed too quckly
                // to ensure data sent to motors is not corrupted
                motorAllStop();
                delay(50);
                restoreMotorPositions(positions);
                rotMoveGrabMode = 2;
                // TODO: Add dynamic calibration system feedback calculation here;
            }
            return 0;
        
        // calculate movement target and start moving forward
        case 2 :
            centimeters = command_buffer[command_index + 2];
            
            if (centimeters == 0){
                rotMoveGrabMode = 0;
                return 1;
            }
            // calculate rotary encoder target based on motion constant
            rotaryTarget = (int) (MOTION_CONST * centimeters);
            
            restoreMotorPositions(positions);
            testForward();
             
            rotMoveGrabMode = 3;
            return 0;

        // perform movement
        case 3 :
            if (-1 * positions[MOTOR_LFT] < rotaryTarget && positions[MOTOR_RGT] < rotaryTarget){
                updateMotorPositions(positions);
                //if (rotaryTarget - (-1 * positions[MOTOR_LFT] + positions[MOTOR_RGT]) / 2 < 40 * MOTION_CONST ){
                //  motorBackward(GRABBER, GRABBER_POWER);
                //  finishGrabbing = 1;
                //}
                return 0;
            }
            else{
                motorAllStop();
                restoreMotorPositions(positions);
                rotMoveGrabMode = 0;
                return 1;
            }
        default:
            return -1;
            break;       
    }
}
int holoMoveStep(){
    // TODO: Add rotational values and feedback
    // TODO: Scale motor values by 1 / abs(value1, value2, value3)
    // to make sure motors are running as fast as possible since
    // maths functions may produce vectors not properly scaled to 1

    int value1 = command_buffer[command_index + 1];
    int value2 = command_buffer[command_index + 2];

    int rot_degrees = (int) value1 + (int) value2;
    float rot_radians = rot_degrees * PI / 180;

    float vx = cos(rot_radians);
    float vy = sin(rot_radians);
    
    float m1_val = -1 * sin(30  * PI / 180)  * vx + cos(30 * PI / 180)  * vy;
    float m2_val = -1 * sin(150 * PI / 180) * vx + cos(150 * PI / 180) * vy;
    float m3_val = -1 * sin(270 * PI / 180) * vx + cos(270 * PI / 180) * vy;
    
    m1_val *= 255;
    m2_val *= 255;
    m3_val *= 255;

    if (m1_val > 0)
        motorForward(1, byte(m1_val));
    else
        motorBackward(1, byte(fabs(m1_val)));
    
    if (m2_val > 0)
        motorForward(0, byte(m2_val));
    else
        motorBackward(0, byte(fabs(m2_val)));
    
    if (m3_val > 0)
        motorForward(2, byte(m3_val));
    else
        motorBackward(2, byte(fabs(m3_val)));    
    delay(1500);
    
    motorAllStop();
    
    return 1;
}

int kickStep(){
    byte kick_val;
    switch(rotMoveGrabMode){
        // initial state which starts ungrabbing
        case 0:
            command_time = millis();
            motorBackward(GRABBER, GRABBER_POWER);
            rotMoveGrabMode = 1;
            return 0;
        // if done with ungrabbing, start kicking
        case 1:
            if (millis() - command_time > GRAB_TIME){
                motorBackward(GRABBER, 0);
                motorForward(KICKER, (int) command_buffer[command_index + 1]);
                rotMoveGrabMode = 2;
                command_time = millis(); // restore current time
            }
            return 0;
        // if done with kicking - start "un-kicking"
        case 2:
            if (millis() - command_time > KICK_TIME){
                motorBackward(KICKER, 189);
                rotMoveGrabMode = 3;
                command_time = millis(); // restore current time
            }
            return 0;
        // if done with "un-kicking" - re-grab
        case 3:
            if (millis() - command_time > KICK_TIME){
                motorBackward(KICKER, 0);
                motorForward(GRABBER, GRABBER_POWER);
                rotMoveGrabMode = 4;
                command_time = millis(); // restore current time
            }
            return 0;
        // if re-grabbed, process is finished
        case 4:
            if (millis() - command_time > GRAB_TIME){
                motorForward(GRABBER, 0);
                rotMoveGrabMode = 0;
                return 1; // make sure that the only way to return from this function is to 
            }
            return 0;
        default:
            Serial.println("BAD KICK");
            rotMoveGrabMode = 0;
            Serial.print(CMD_ERROR);
            return -1;
    }
    return -1;
}

int grabStep(){
    switch(rotMoveGrabMode){
        case 0:
            motorForward(GRABBER, GRABBER_POWER);
            command_time = millis();
            rotMoveGrabMode = 1;
            return 0;
        case 1:
            if (millis() - command_time > GRAB_TIME){
                motorForward(GRABBER, 0);
                rotMoveGrabMode = 0;
                finishGrabbing = 0;
                return 1;
            }
            return 0;
    }
}

int unGrabStep(){
    switch(rotMoveGrabMode){
        case 0:
            motorBackward(GRABBER, GRABBER_POWER);
            command_time = millis();
            rotMoveGrabMode = 1;
            return 0;
        case 1:
            if (millis() - command_time > GRAB_TIME){
                motorBackward(GRABBER, 0);
                rotMoveGrabMode = 0;
                return 1;

            }
            return 0;
    }
}

float calculateRotaryTarget(float x3){
    // linear function approximation, e.g. finding y3 based on y1, y2, x1, x2, x3
    // for fixed rotational value calibrations
    
    // TODO: Add values for dynamic calibration in each state based
    // on overshoot/undershoot and compass/gyro feedback for each 
    // approximation case

    float x1, x2;
    float y1, y2;
    
    if (x3 <= 30) {
        x1 = 0;
        x2 = 30;
        y1 = 0;
        y2 = 1.55;
    } else if (x3 <= 45){
        x1 = 30;
        x2 = 45;
        y1 = 1.55;
        y2 = 1.75;
    } else if (x3 <= 60){
        x1 = 45;
        x2 = 60;
        y1 = 1.75;
        y2 = 1.95;
    } else if (x3 <= 90){
        x1 = 60;
        x2 = 90;
        y1 = 1.95;
        y2 = 2.17;
    } else if (x3 <= 120){
        x1 = 90;
        x2 = 120;
        y1 = 2.17;
        y2 = 2.85;
    } else if (x3 <= 180){
        x1 = 120;
        x2 = 180;
        y1 = 2.85;
        y2 = 3.675;
    } else {
        return 4;
    }
    return y1 + (y2 - y1) * ((x3 - x1) / (x2 - x1));
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






