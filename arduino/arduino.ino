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
#define CMD_HOLMOVE    B00000010 // Buffered
#define CMD_KICK       B00000100 // Buffered
#define CMD_STOP       B00001000 // Buffered
#define CMD_GRAB       B00010000 // Buffered
#define CMD_UNGRAB     B00100000 // Buffered
#define CMD_FLUSH      B01000000 // Immediate. Flushes the buffer and awaits new commands
/* Sent by Arduino*/
//define CMD_END        B11111101 // Buffered
#define CMD_ERROR      B11111111 // Sent for errors
#define CMD_FULL       B11111110 // Sent if buffer is full
#define CMD_RESEND     B11111100 // if all commands haven't been received in 500 miliseconds
#define CMD_ACK        B11111010 // Sent after command has been received
#define CMD_FIN        B11111101 // Sent when command is finished

// Comms Tuning Parameters
#define RESPONSE_COUNT 3 // how many bytes to respond with, for ACK and FIN
#define RESPONSE_PERIOD 10 // how many milliseconds to wait between responses
byte SEQ_NUM = 0; // Sequence number, flipped between 1 and 0

// utils
#define BUFFERSIZE 256
#define ROTARY_COUNT 3
#define IDLE_STATE 0
#define MAG_OFFSET_X 312
#define MAG_OFFSET_Y 3605


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
byte invalid_commands = 0;

// used for the millis function.
unsigned long serial_time; 
unsigned long command_time;
unsigned long idle_time;
unsigned long report_time;
unsigned long re_ack_time; // TODO: Remove

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
boolean left_correction = 0;
boolean right_correction = 0;

// accelerometer variables
float accel_targetx = 0;
float accel_targety = 0;

// compass targets
float target_angle;
float angle_difference;

// Accelerometer/Magnetometer values
int mag_min_x; // for caliration
int mag_max_x; // for caliration
int mag_min_y; // for caliration
int mag_max_y; // for caliration
int accel[3];                // we'll store the raw acceleration values here
int mag[3];                  // raw magnetometer values stored here
float realAccel[3];          // calculated acceleration values here
float heading, titleHeading; // compass values stored here

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
    report_time = millis();

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
    
    mag_min_x = mag[0];
    mag_max_x = mag[0];
    mag_min_y = mag[1];
    mag_max_y = mag[1];
    
    /* Custom commands can be initialized below */
    /*command_buffer[0] = CMD_ROTMOVE;
    command_buffer[1] = 10;
    command_buffer[2] = 0;
    command_buffer[3] = 255;
    buffer_index = 4;*/
    delay(300); // delay to get first proper mag value
  }
  

void loop() {
  // Communication FSM part
  Communications();
  CommsOut();
  // Sensor FSM part
  
  pollAccComp();
  

  // ***** Compass Calibration part
  //calibrateCompass(); // if wanting to do per-pitch calibration
  /*if (millis() - idle_time < 3000){
      Serial.println(sqrt(realAccel[0] * realAccel[0]  + realAccel[1] * realAccel[1]));
      Serial.println(heading);
  }*/
  //delay(1000);


  // Action FSM part
  int state_end = 0;

  // remove SEQ from command
  MasterState = MasterState & 127;

  if (MasterState != IDLE_STATE){
      re_ack_time = millis();
  }

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
        
        // make not of respond time
        re_ack_time = millis();

      
    }
}


int calculateChecksum(int target_value){
    int i, j, check = 0;
    for (i = target_value - 4; i < target_value - 1; i++){
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


void Communications() {
    // for targetting buffer checks so as not to do buffer[0 - 1]
    int target_value;
    byte checksum = 0;
    char garbage;
    
    // to make sure Serial reading can get interrupted
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

            checksum = byte(calculateChecksum(target_value));

            // check for SEQ number and checksum to find if command is valid
            if (((command_buffer[target_value - 4] & 128) == 128 * SEQ_NUM) && 
                (command_buffer[target_value - 1] == checksum)){
                
                invalid_commands = 0;
                SEQ_NUM = SEQ_NUM == 1 ? 0 : 1;

                // Cases for Atomic commands
                if (command_buffer[target_value - 4] == CMD_FLUSH){
                    restoreState();
                }
                else if (command_buffer[target_value - 4] == CMD_STOP){
                    motorAllStop();
                    rotMoveGrabMode = 0;
                    MasterState = 0;
                    bufferOverflow = 0;
                    commandOverflow = 0;
                }    
            }
            // report invalid command
            else{
                invalid_commands += 1;
                buffer_index = target_value - 4;
                
                if (buffer_index == 252){
                    bufferOverflow -= 1;
                }

                while(Serial.available()){
                    garbage = Serial.read();
                    //Serial.write(garbage);
                }
                /*
                if (invalid_commands >= 10){
                    //for (int i=0; i < RESPONSE_COUNT; i++){
                    //    Serial.write(CMD_ACK);
                    //    delay(RESPONSE_PERIOD);
                    }
                    invalid_commands = 0;
                }*/
            }
        }
        // Time-out serial if reading is taking too long
        else if (millis() - serial_time > 200){ 
            Serial.write(CMD_FULL);
            while(buffer_index %4 != 0) {
                buffer_index--;
            }
        }
    }
}

void CommsOut(){
    byte args[6], checksum = 0;
    if (millis() - report_time > 250){
        args[0] = CMD_FIN;
        args[1] = bufferOverflow;
        args[2] = buffer_index;
        args[3] = command_index;
        if (heading > 180) {
            args[4] = 180;
            args[5] = byte(int(heading - 180));
        }
        else{
            args[4] = byte(int(heading));
            args[5] = 0;
        }
        for (int i = 0; i < 6; i++){
            checksum += (args[i] & 1);
            checksum += (args[i] & 2)   >> 1;
            checksum += (args[i] & 4)   >> 2;
            checksum += (args[i] & 8)   >> 3;
            checksum += (args[i] & 16)  >> 4;
            checksum += (args[i] & 32)  >> 5;
            checksum += (args[i] & 64)  >> 6;
            checksum += (args[i] & 128) >> 7;
        }
        for (int i = 0; i < 6; i++){
            Serial.write(args[i]);
            delay(5);
        }
        Serial.write(255 - checksum);
        report_time = millis();
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
    
    // wait for the magnetometer readings to be ready
    // if they're not - get them at next main loop
    if(Lsm303d.isMagReady()){
        // get the magnetometer values, store them in mag
        Lsm303d.getMag(mag);
        // uncomment during calibration
        mag[0] += MAG_OFFSET_X;
        mag[1] += MAG_OFFSET_Y;
        //for (int i = 0; i < 3; i++){
        //  mag[i] -= mag_offset[i];
        //}
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
    int left, left_angle, right_angle;
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
            
            /** Use bottom commented-out code for rotary stuff */
            // calculate target based on piece-wise linear approximation for
            // know values of 30, 45, 60, 90, 120, 180 degrees
            //rotaryTarget = (int) (calculateRotaryTarget(degrees) * degrees);  
            // restore and update motor positions to account for initial bias
            // based on wheels & rotary encoders;
            //restoreMotorPositions(positions);
            //updateMotorPositions(positions);
            //rotaryBias = positions[0] + positions[1] + positions[2];
            
            target_angle = normalize_angle(titleHeading - (float(degrees) * left));
            
            // got straight to correction for low angles
            
            if (left == 1)
                rotateLeft();
            else
                rotateRight();

            rotMoveGrabMode = 1;
            
            // manual override for VERY small angles
            if (degrees < 15){
                delay(degrees * 25);
                motorAllStop();
                rotMoveGrabMode = 2;
                return 0;
            }

            return 0;
        
        // chck whether to stop during rotation;
        case 1 :
            left = (MasterState >> 3) & 127; // left becomes MSB of master state/current command
            left = left == 0 ? 1 : -1;
            
            angle_difference = calculateAngleDifference(heading, target_angle);
            degrees = command_buffer[command_index + 1];
            
            if (angle_difference < 10){
                motorAllStop();
                rotMoveGrabMode = 4;
                delay(150);
                command_time = millis();
            }
            
            else{
                // delay to make sure motor actions are not being performed too quckly
                // to ensure data sent to motors is not corrupted
                updateMotorPositions(positions);
                rotMoveGrabMode = 1;
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
            delay(75);
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

        // rotation correction
        case 4 :
            if (millis() - command_time > 850){
                motorAllStop();
                rotMoveGrabMode = 2;
            }
            else if (calculateAngleDifference(heading, target_angle) > 5){
                left_angle = calculateLeftAngle(heading, target_angle);
                right_angle = calculateRightAngle(heading, target_angle);
                if (left_angle < right_angle){
                    right_correction = 1;
                    left_correction = 0;
                    correctRight();
                }
                else {
                    right_correction = 0;
                    left_correction = 1;
                    correctLeft();
                }
            }
            else{
                motorAllStop();
          }
          return 0;
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
    
    float scale_factor = fmax(abs(m1_val), abs(m2_val));
    scale_factor = 1 / fmax(scale_factor, abs(m3_val));
    
    // scale up to 1
    m1_val *= scale_factor;
    m2_val *= scale_factor;
    m3_val *= scale_factor;
    
    //scale up to 255
    m1_val *= POWER_RGT;
    m2_val *= POWER_LFT;
    m3_val *= POWER_BCK;
    
    // turn motors
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

float normalize_angle(float angle){
    if (angle > 360)
        angle -= 360;
    
    else if (angle < 0)
        angle += 360;
    
    return angle;
}

int calculateAngleDifference(float current_angle, float target_angle){
    int phi = abs(int(target_angle - current_angle)) % 360;
    if (phi > 180)
        return 360 - phi;
    else
        return phi;
}

int calculateLeftAngle(float current_angle, float target_angle){
    int phi = abs(int(target_angle - current_angle)) % 360;
    if (current_angle < target_angle)
        return phi;
    else
        return 360 - phi;
}

int calculateRightAngle(float current_angle, float target_angle){
    int phi = abs(int(target_angle - current_angle)) % 360;
    if (current_angle < target_angle)
        return 360 - phi;
    else
        return phi;
}

void calibrateCompass(){ 
  if (mag[0] > mag_max_x){
      mag_max_x = mag[0];
  }
  if (mag[0] < mag_min_x){
      mag_min_x = mag[0];
  }
  if (mag[1] > mag_max_y){
      mag_max_y = mag[1];
  }
  if (mag[1] < mag_min_y){
      mag_min_y = mag[1];
  }

  if (millis() - idle_time > 5000){
    idle_time = millis();
    Serial.print("MIN X: ");
    Serial.println(mag_min_x);
    Serial.print("MAX X: ");
    Serial.println(mag_max_x);
    Serial.print("MIN Y: ");
    Serial.println(mag_min_y);
    Serial.print("MAX Y: ");
    Serial.println(mag_max_y);
    Serial.print("BIAS_X: ");
    Serial.println(-0.5 * (mag_max_x + mag_min_x));
    Serial.print("BIAS_Y: ");
    Serial.println(-0.5 * (mag_max_y + mag_min_y));
    
 }
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
    motorBackward(MOTOR_LFT, (int)(POWER_LFT * 1));
    motorBackward(MOTOR_RGT, (int)(POWER_RGT * 1));
    motorBackward(MOTOR_BCK, (int)(POWER_BCK * 1));    
}

void correctRight(){
    motorBackward(MOTOR_LFT, (int)(POWER_LFT * 0.7));
    motorBackward(MOTOR_RGT, (int)(POWER_RGT * 0.7));
    motorBackward(MOTOR_BCK, (int)(POWER_BCK * 0.7));    
}

void rotateLeft() {
    motorForward(MOTOR_LFT, (int)(POWER_LFT * 1));
    motorForward(MOTOR_RGT, (int)(POWER_RGT * 1));
    motorForward(MOTOR_BCK, (int)(POWER_BCK * 1));    
}

void correctLeft(){
    motorForward(MOTOR_LFT, (int)(POWER_LFT * 0.7));
    motorForward(MOTOR_RGT, (int)(POWER_RGT * 0.7));
    motorForward(MOTOR_BCK, (int)(POWER_BCK * 0.7));    
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
