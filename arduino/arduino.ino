#include "B4SDP.h"
#include "Arduino.h"
#include <Math.h>
#include <Wire.h>
#include "Accelerometer_Compass_LSM303D.h"
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
#define CMD_ROTMOVE    B00000011 // Buffered: MSB 1 performs CCW rotation
#define CMD_ROTMOVECCW B00001111 // Buffered: MSB 1 performs CCW rotation
#define CMD_HOLMOVE    B00000010 // Buffered: NOT YET IMPLEMENTED
#define CMD_KICK       B00000100 // Buffered
#define CMD_STOP       B00001000 // Buffered
#define CMD_GRAB       B00010000 // Buffered
#define CMD_UNGRAB     B00100000 // Buffered
#define CMD_FLUSH      B01000000 // Immediate. Flushes the buffer and awaits new commands
/* Sent by Arduino*/
//define CMD_END        B11111101 // Buffered
#define CMD_DONE       B11111101 // Sent when command is finished
#define CMD_ERROR      B11111111 // Sent for errors
#define CMD_FULL       B11111110 // Sent if buffer is full
#define CMD_RESEND     B11111100 // if all commands haven't been received in 500 miliseconds
#define CMD_ACK        B11111010 // Sent after command has been received


// utils
#define BUFFERSIZE 256
#define ROTARY_COUNT 3
#define IDLE_STATE 0
byte SEQ_NUM = 0;

// *** Globals ***
// A finite state machine is required to provide concurrency between loop, sensor_poll and 
// serialEvent functions which both support reading serial while moving and
// rotary-encoder-based motion, plus sensor data-gathering

byte MasterState = 0;
byte finishGrabbing = 0;
byte rotMoveGrabMode = 0;

// positions of wheels based on rotary encoder values
int positions[ROTARY_COUNT] = {0};


// circular command buffer
byte command_buffer[BUFFERSIZE];
byte buffer_index = 0; // current circular buffer utilization index
byte command_index = 0; // current circular buffer command index
byte bad_commands = 0;

// used for the millis function.
unsigned long serial_time;
unsigned long serial_deriv; 
unsigned long command_time;
unsigned long idle_time;
// rotation parameters
int rotaryTarget;
int rotaryBias;


// circular buffer counters
byte bufferOverflow = 0;
byte commandOverflow = 0;


// targets for rotary encoders
int rotary_target;
int motion_target;
int holono_target;

// accelerometer variables
float accel_targetx = 0;
float accel_targety = 0;

float accel_offsetx = 0;
float accel_offsety = 0;

// compass targets
float start_angle;
float target_angle;
float previous_gyro;


// Accelerometer/Compass values
int accel[3];               // we'll store the raw acceleration values here
int mag[3];                 // raw magnetometer values stored here
float realAccel[3];         // calculated acceleration values here
float heading, titleHeading;

int calculateChecksum(int target_value){
    int i, j, check = 0;
    for (i = target_value - 4; i < target_value - 1; i++){
        //for (j = 0; j < 8; j++){
        //    check += bitRead(command_buffer[i], j);
        //}
        check += (command_buffer[i] & 1);
        check += (command_buffer[i] & 2)   >> 1;
        check += (command_buffer[i] & 4)   >> 2;
        check += (command_buffer[i] & 8)   >> 3;
        check += (command_buffer[i] & 16)  >> 4;
        check += (command_buffer[i] & 32)  >> 5;
        check += (command_buffer[i] & 64)  >> 6;
        check += (command_buffer[i] & 128) >> 7;
    }
    return 255 - check;
}


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
    idle_time = millis();

    /*********** Uncomment for Sensors *****************
    // initialize Accelerometer/Compass sensor
    char init = 0;
    init = Lsm303d.initI2C();
    
    // get initial Accelerometer/Compass Data
    Lsm303d.getAccel(accel);
    
    while(!Lsm303d.isMagReady());// wait for the magnetometer readings to be ready
    Lsm303d.getMag(mag);  // get the magnetometer values, store them in mag
    
    // X:0, Y:1, Z:2 for index:axis
    for (int i=0; i<3; i++)
    {
        realAccel[i] = accel[i] / pow(2, 15) * ACCELE_SCALE;  // calculate real acceleration values, in units of g
    }
    // angle between X and north
    heading = Lsm303d.getHeading(mag);
    // tilt-compensated angl
    titleHeading = Lsm303d.getTiltHeading(mag, realAccel);
    
    // remember offset gyro-values
    accel_offsetx = realAccel[0];
    accel_offsety = realAccel[1];
    *********** Uncomment for Sensors END **************/

    /* Custom commands can be initialized below */
    
  }

void loop() {
  Communications();
  // get sensor data at each time-step
  //pollAccComp();
  int state_end = 0;
  MasterState = MasterState & 127;
  
  // Switch statement for the FSM state
  switch(MasterState){
        
        case IDLE_STATE:
            // very strange issue fix
            if (command_index > buffer_index && commandOverflow == bufferOverflow){
                command_index = buffer_index;
            }
            // check whether circular buffer contains a valid command
            if ((command_index != buffer_index && command_index + 4 <= buffer_index && commandOverflow == bufferOverflow) || 
                 commandOverflow < bufferOverflow) {
                MasterState = command_buffer[command_index];
                restoreMotorPositions(positions);
                command_time = millis(); // for time-out

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
            Serial.write(CMD_ERROR);
            Serial.write(CMD_ERROR);
            Serial.write(CMD_ERROR);
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
      
    for (int i=0; i < 8; i++){
        Serial.write(CMD_DONE);
        delay(10);
    }
      //delay(5000);
      
     }
    /*
    if (millis() - idle_time > 3000 && command_index != 0){
        Serial.write(rotMoveGrabMode);
        Serial.write(MasterState);
        Serial.write(SEQ_NUM);
        idle_time = millis();
        if (buffer_index != CMD_DONE && buffer_index != CMD_ACK){
            Serial.write(buffer_index);
        }
        if (command_index != CMD_DONE && command_index != CMD_ACK){
            Serial.write(command_index);
        }
    }*/
    // add this in before and set state_end to 1
    if (millis() - serial_time > 5000 && command_index != 0){

       for (int i=0; i < 8; i++){
            Serial.write(CMD_DONE);
            delay(10);
        }
       serial_time = millis();

    }
}

/* 
SerialEvent occurs whenever a new data comes in the
hardware serial RX. This routine is run between each
time loop() runs.
*/

void Communications() {
    // for targetting buffer checks so as not to do buffer[0 - 1]
    int target_value;
    byte checksum = 0;
    char garbage;
    // to make sure Serial reading can get interrupted
    
    serial_deriv = millis();
    while (Serial.available()) {
        serial_time = millis();
        // note overflow to maintain circular buffer
        if (buffer_index == 255){
            bufferOverflow++;
        }
        
        // read command
        command_buffer[buffer_index++] = Serial.read();
        Serial.write(command_buffer[buffer_index - 1]);
        if (buffer_index % 4 == 0){
            
            // acknowledge proper command
            if (buffer_index == 0){
                target_value = 256;
            } else {
                target_value = buffer_index;
            }

            checksum = byte(calculateChecksum(target_value));

            // check for SEQ number and checksum
            if (((command_buffer[target_value - 4] & 128) == 128 * SEQ_NUM) && 
                (command_buffer[target_value - 1] == checksum)){
                
                SEQ_NUM = SEQ_NUM == 1 ? 0 : 1;
                for (int i=0; i < 8; i++){
                    Serial.write(CMD_ACK);
                    delay(10);
                }

                //Serial.write(command_index / 4);
                //Serial.write(buffer_index / 4);
                //Serial.write(command_buffer[target_value - 4]);
                //Serial.write(command_buffer[target_value - 3]);
                //Serial.write(command_buffer[target_value - 2]);
                //Serial.write(command_buffer[target_value - 1]);
                 
                if (command_buffer[target_value - 4] == CMD_FLUSH){
                    restoreState();
                } else if (command_buffer[target_value - 4] == CMD_STOP){
                    motorAllStop();
                    rotMoveGrabMode = 0;
                    MasterState = 0;
                    bufferOverflow = 0;
                    commandOverflow = 0;
                }    
            }
                // report bad command
            else{
                bad_commands += 1;
                Serial.write(CMD_ERROR);
                Serial.write(SEQ_NUM);
                Serial.write(CMD_ERROR);

                buffer_index -= 4;
                while(Serial.available()){
                    garbage = Serial.read();
                    //Serial.write(garbage);
                }
                if (bad_commands >= 30){
                    for (int i=0; i < 8; i++){
                        Serial.write(CMD_ACK);
                        delay(10);
                    }
                    bad_commands = 0;
                }
            }
        }
        else if (millis() - serial_deriv > 500){ // TODO: Break this only here;
            //Serial.write("Time-Out");
            Serial.write(CMD_FULL);
            while(buffer_index %4 != 0) {
                buffer_index--;
            }
        }
    }
}

void pollAccComp(){

    // calculate real acceleration values, in units of g
    // X:0, Y:1, Z:2 for index:axis
    Lsm303d.getAccel(accel);
    for (int i=0; i<3; i++)
        {
            realAccel[i] = accel[i] / pow(2, 15) * ACCELE_SCALE;
        }
    //realAccel[0] -= accel_offsetx;
    //realAccel[1] -= accel_offsety;
    
    // wait for the magnetometer readings to be ready
    if(Lsm303d.isMagReady()){

        // get the magnetometer values, store them in mag
        Lsm303d.getMag(mag);
        
        // angle between X and north
        heading = Lsm303d.getHeading(mag);
        
        // tilt-compensated angle
        titleHeading = Lsm303d.getTiltHeading(mag, realAccel);
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
            left = (MasterState >> 3) & 127; // left becomes MSB of master state/current command
            left = left == 0 ? 1 : -1;

            if (!degrees){
                rotMoveGrabMode = 2;
                return 0;
            }
            rotMoveGrabMode = 1;
            // calculate target based on piece-wise linear approximation for
            // know values of 30, 45, 60, 90, 120, 180 degrees
            rotaryTarget = (int) (calculateRotaryTarget(degrees) * degrees);  
            
            // restore and update motor positions to account for initial bias
            // based on wheels & rotary encoders;
            restoreMotorPositions(positions);
            updateMotorPositions(positions);
            rotaryBias = positions[0] + positions[1] + positions[2];

            // *uncomment for using compass
            //start_angle = titleHeading;
            //target_angle = float(degrees);

            if (left == 1)
                rotateLeft();
            else
                rotateRight();
            
            return 0;
        
        // chck whether to stop during rotation;
        case 1 :
            left = (MasterState >> 3) & 127; // left becomes MSB of master state/current command
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
            }
            return 0;
        
        // calculate movement target and start moving forward
        case 2 :
            centimeters = command_buffer[command_index + 2];
            command_time = millis();
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
            centimeters = command_buffer[command_index + 2];
            if ((millis() - command_time > 1500) && centimeters < 35){
                motorAllStop();
                restoreMotorPositions(positions);
                rotMoveGrabMode = 0;
                return 1;
            }
            if (-1 * positions[MOTOR_LFT] < rotaryTarget && positions[MOTOR_RGT] < rotaryTarget){
                updateMotorPositions(positions);
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
    // TODO: Scale motor values by 1 / max: abs(value1, value2, value3)
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
            //Serial.writeln("BAD KICK");
            rotMoveGrabMode = 0;
            Serial.write(CMD_ERROR);
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
        x1 = 0.75;
        x2 = 30;
        y1 = 0;
        y2 = 1.7;
    } else if (x3 <= 45){
        x1 = 30;
        x2 = 45;
        y1 = 1.7;
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
void fullMotorTest(){
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
