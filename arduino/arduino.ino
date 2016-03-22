#include "B4SDP.h"
#include "Arduino.h"
#include <Math.h>
#include <Wire.h>
#include "Accelerometer_Compass_LSM303D.h"


// Motor Definitions
#define MOTOR_LFT   3
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


// temporal calibrations for grabber/ kicker
#define KICK_TIME 550
#define GRAB_TIME 650


// Movement and kicker Constants
#define MOTION_CONST 11.891304
#define ROTATION_CONST 0.4
#define ROTATION_CORRECT_TIME 400
#define KICKER_CONST 10.0  


/****** COMMS API Byte Definitions  ******/
#define CMD_ROTMOVE    B00000011 // Buffered. Bits 2-3 indicate direction 
#define CMD_ROTMOVECCW B00001111 // Buffered. Bits 2-3 indicate direction

#define CMD_STOP       B00001000 // Atomic.
#define CMD_KICK       B00000100 // Buffered.
#define CMD_GRAB       B00010000 // Buffered or atomic dependent on next byte
#define CMD_UNGRAB     B00100000 // Buffered or atomic dependent on next byte
#define CMD_FLUSH      B01000000 // Immediate. Flushes the buffer and awaits new commands

#define CMD_HOLMOVE_1  B01111100 // Buffered. May be corrected via the same command. First 2 bits part of args
#define CMD_HOLMOVE_2  B01111101 // Buffered. May be corrected via the same command. First 2 bits part of args
#define CMD_HOLMOVE_3  B01111110 // Buffered. May be corrected via the same command. First 2 bits part of args
#define CMD_HOLMOVE_4  B01111111 // Buffered. May be corrected via the same command. First 2 bits part of args

#define CMD_FIN        B11111101 // Sent  back based on response time for encoded state representation feedback


// Comms Tuning Parameters
#define RESPONSE_TIME 200
byte SEQ_NUM = 0; // Sequence number, flipped between 1 and 0


// utils
#define BUFFERSIZE 256
#define ROTARY_COUNT 3
#define IDLE_STATE 0


#define COMPASS_CALIBRATION_TIME 4000
int MAG_OFFSET_X = 0;
int MAG_OFFSET_Y = 0;
int MAG_OFFSET_Z = 0;


// *** Globals ***
// A finite state machine is required to provide concurrency between loop, sensor_poll and 
// serialEvent functions which both support reading serial while moving and
// rotary-encoder-based motion, plus sensor data-gathering
byte MasterState = 0;
byte finishGrabbing = 0;
byte MoveMode = 0;
byte GrabMode = 0;
boolean AtomicGrab = 0;
byte AtomicGrabMode = 0;
boolean AtomicUnGrab = 0;
byte AtomicUnGrabMode = 0;
boolean GrabberStatus = 0;


// positions of wheels based on rotary encoder values
int positions[ROTARY_COUNT] = {0};


// circular command buffer
byte command_buffer[BUFFERSIZE];
byte buffer_index = 0; // current circular buffer utilization index
byte command_index = 0; // current circular buffer command index
byte invalid_commands = 0;


// temporal parameters used for the millis function.
unsigned long serial_time;  // to make sure serial isn't flooded
unsigned long command_time; // to make sure commands can be interrupted
unsigned long idle_time;    // to make compass calibration possible
unsigned long report_time;  // to make reporting state possible
unsigned long atomic_time;  // to make sure atomic grab/ungrab may be performed
unsigned long correct_time; // to enable rotational correction optimization

// holonomic parameters
int holo_vals[3];

// rotation parameters
int rotaryTarget;
int rotaryBias;
byte in_the_zone = 0;

// circular buffer counters
byte bufferOverflow = 0;
byte commandOverflow = 0;


// parameter targets for rotary encoders
int rotary_target;
int motion_target;
int holono_target;


// accelerometer variables
float accel_targetx = 0;
float accel_targety = 0;

// compass targets
float target_angle;
float angle_difference;

// Accelerometer/Magnetometer values
int mag_min_x; // for calibration
int mag_max_x; // for calibration
int mag_min_y; // for calibration
int mag_max_y; // for calibration
int mag_min_z; // for calibration
int mag_max_z; // for calibration
byte calibrate_compass;

int accel[3];                // we'll store the raw acceleration values here
int mag[3];                  // raw magnetometer values stored here
float realAccel[3];          // calculated acceleration values here
float heading, titleHeading; // compass values stored here


void restoreState(){
    updateMotorPositions(positions);
    restoreMotorPositions(positions);
    buffer_index = 0;
    command_index = 0;
    bufferOverflow = 0;
    commandOverflow = 0;
    MoveMode = 0;
    finishGrabbing = 0;
    MasterState = 0;
    motorAllStop();
    idle_time = millis();
    report_time = millis();
    atomic_time = millis();
}

// Main Functions: Setup, Loop and SerialEvent
void setup() {
    SDPsetup();
    restoreState();
    
    // initialize Accelerometer/Compass sensor and get initial bias vals
    char init = 0;
    init = Lsm303d.initI2C();
    
    
    // get initial Accelerometer/Compass Data
    Lsm303d.getAccel(accel);
    while(!Lsm303d.isMagReady());// wait for the magnetometer readings to be ready
    Lsm303d.getMag(mag);  // get the magnetometer values, store them in mag
    for (int i=0; i<3; i++){
        realAccel[i] = accel[i] / pow(2, 15) * ACCELE_SCALE;  
    }
    heading = Lsm303d.getHeading(mag);
    titleHeading = Lsm303d.getTiltHeading(mag, realAccel);
    
    // compass calibration parameters. At the beginning the robot will rotate left.
    mag_min_x = mag[0];
    mag_max_x = mag[0];
    mag_min_y = mag[1];
    mag_max_y = mag[1];
    mag_min_z = mag[2];
    mag_max_z = mag[2];
    calibrate_compass = 1;
    correctLeft();
    delay(300); // delay to get first proper mag value
    
    /* Custom commands can be initialized below */
    /*command_buffer[0] = CMD_HOLMOVE_4;
    command_buffer[1] = 35;
    command_buffer[2] = 35;
    command_buffer[3] = 255;
    buffer_index = 4;*/
  }
  

void loop() {
    int state_end = 0;
  
    // automatic compass calibration first time arduino is turned on
    if (calibrate_compass){
        if (millis() - idle_time < COMPASS_CALIBRATION_TIME)
            calibrateCompass();
        else{
            calibrate_compass = 0;
            motorAllStop();
        }
        return;
    } 

    // Comms in and out
    Communications();
    CommsOut();
  
    // Sensor FSM part
    pollAccComp();
    updateMotorPositions(positions);

    // Action fsm part
    // remove SEQ from command
    handleAtomicActions();
    MasterState = MasterState & 127;
    switch(MasterState){
            
        case IDLE_STATE:

            // check whether circular buffer contains a valid command
            if ((command_index != buffer_index && command_index + 4 <= buffer_index && commandOverflow == bufferOverflow) || 
                 commandOverflow < bufferOverflow) {
                MasterState = command_buffer[command_index];
                restoreMotorPositions(positions);
            }
            command_time = millis(); // for time-out
            break;
        

        case CMD_ROTMOVE:
            state_end = rotMoveStep();
            break;
        

        case CMD_ROTMOVECCW:
            state_end = rotMoveStep();
            break;
        

        case CMD_HOLMOVE_1:
            state_end = holoMoveStep();
            break;
        
        case CMD_HOLMOVE_2:
            state_end = holoMoveStep();
            break;

        case CMD_HOLMOVE_3:
            state_end = holoMoveStep();
            break;
        
        case CMD_HOLMOVE_4:
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
            MasterState = IDLE_STATE;
            state_end = 1;
            break;
    }
  if (millis() - command_time > 5000)
      state_end = 1;

  if (state_end ){
        motorAllStop();
        MasterState = IDLE_STATE;
        command_index += 4;

      // check for circular buffer end
      if (command_index == 0){
          commandOverflow++;
      }
      // override report_time to respond immediately!
      report_time += RESPONSE_TIME + 1;
      CommsOut();
      
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

void atomicHoloCommand(byte target_value){

    if ((command_buffer[target_value - 8] ^ CMD_HOLMOVE_1) <= 3){
        for (int i = 0; i < 4; i++){
            // copy new command into previous command
            command_buffer[target_value - 8 + i] = command_buffer[target_value - 4 + i];
            command_time = millis();
        }
        restoreCommsState(target_value);
    }

}
void restoreCommsState(byte target_value){
    buffer_index = target_value - 4;
    bufferOverflow = buffer_index == 252 ? bufferOverflow - 1 : bufferOverflow;  
    SEQ_NUM = SEQ_NUM == 1 ? 0 : 1;
}


void Communications() {
    // for targetting buffer checks so as not to do buffer[0 - 1]
    int target_value;
    byte checksum = 0, command_id;
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
                command_id = command_buffer[target_value - 4] & 127;
                command_buffer[target_value - 4] = command_id;
                // handle atomic operations
                switch(command_id){
                    case CMD_FLUSH:
                        restoreState();
                        break;

                    
                    case CMD_STOP:
                        motorAllStop();
                        MoveMode = 0;
                        MasterState = 0;
                        command_index = target_value;
                        commandOverflow = bufferOverflow;
                        break;
                    
                    case CMD_GRAB:
                        if (command_buffer[target_value - 3]){
                            AtomicGrab = 1;
                            restoreCommsState(target_value);
                        }
                        break;
                    

                    case CMD_UNGRAB:
                        if (command_buffer[target_value - 3]){
                            AtomicUnGrab = 1;
                            restoreCommsState(target_value);
                        }
                        break;
                    
                    case CMD_HOLMOVE_1:
                        // commsState is restored inside the function
                        atomicHoloCommand(target_value);
                        break;


                    case CMD_HOLMOVE_2:
                        // commsState is restored inside the function
                        atomicHoloCommand(target_value);
                        break;


                    case CMD_HOLMOVE_3:
                        // commsState is restored inside the function
                        atomicHoloCommand(target_value);
                        break;


                    case CMD_HOLMOVE_4:
                        // commsState is restored inside the function
                        atomicHoloCommand(target_value);
                        break;
                }
                /*
                for (int i = 0; i < 4; i++){
                    Serial.print(i);
                    Serial.print(": ");
                    Serial.println(command_buffer[i]);
                }
                Serial.println("===========");
                */    
                report_time += RESPONSE_TIME + 1;
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
            }
        }
        // Time-out serial if reading is taking too long
        else if (millis() - serial_time > 200){ 
            while(buffer_index %4 != 0) {
                buffer_index--;
            }
        }
    }
}

void CommsOut(){
    byte args[7], checksum = 0, checkarg = 0;
    if (millis() - report_time > RESPONSE_TIME){
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
        args[6] == GrabberStatus;

        for (int i = 0; i < 7; i++){
            checkarg += (args[i] & 1);
            checkarg += (args[i] & 2)   >> 1;
            checkarg += (args[i] & 4)   >> 2;
            checkarg += (args[i] & 8)   >> 3;
            checkarg += (args[i] & 16)  >> 4;
            checkarg += (args[i] & 32)  >> 5;
            checkarg += (args[i] & 64)  >> 6;
            checkarg += (args[i] & 128) >> 7;
            checksum += checkarg * (i + 1);
            checkarg = 0
        }
        for (int i = 0; i < 6; i++){
            Serial.write(args[i]);
            delay(5);
        }
        Serial.write(255 - checksum);
        report_time = millis();
    }  
}

void handleAtomicActions(){
    if (AtomicUnGrab){
        switch(AtomicUnGrabMode){
            // start grabbing
            case 0:
                motorForward(GRABBER, GRABBER_POWER);
                AtomicUnGrabMode = 1;
                break;
            

            // finish ungrabbing
            case 1:
                if (millis() - atomic_time > GRAB_TIME){
                    motorForward(GRABBER, 0);
                    AtomicUnGrabMode = 0;
                    AtomicUnGrab = 0;
                    GrabberStatus = 1;
                    atomic_time = millis();
                }
                break;
            

            default:
                break;
        }
    }
    else if (AtomicGrab){
        switch(AtomicGrabMode){
            case 0:
                motorBackward(GRABBER, GRABBER_POWER);
                AtomicGrabMode = 1;
                break;
            

            // finish grabbing
            case 1:
                if (millis() - atomic_time > GRAB_TIME){
                    motorBackward(GRABBER, 0);
                    AtomicGrabMode = 0;
                    AtomicGrab = 0;
                    GrabberStatus = 0;
                    atomic_time = millis();
                }
                break;


            default:
                break;
        }
    }
    else{
        atomic_time = millis();
    }
}

int rotMoveStep(){
    // values for target calculation
    int left, left_angle, right_angle;
    byte degrees, centimeters;

    switch(MoveMode){

        // calculate rotation target and start rotating
        case 0 :
            degrees = command_buffer[command_index + 1];
            left = (MasterState >> 3) & 127; // left becomes MSB of master state/current command
            left = left == 0 ? 1 : -1;

            if (!degrees){
                MoveMode = 2;
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
            
            target_angle = normalize_angle(heading - (float(degrees) * left));
            
            // got straight to correction for low angles
            
            if (left == 1)
                rotateLeft();
            else
                rotateRight();

            MoveMode = 1;
            
            // manual override for VERY small angles
            if (degrees < 15){
                delay(degrees * 25);
                motorAllStop();
                MoveMode = 2;
                return 0;
            }

            return 0;
        
        // chck whether to stop during rotation;
        case 1 :
            left = (MasterState >> 3) & 127; // left becomes MSB of master state/current command
            left = left == 0 ? 1 : -1;
            
            angle_difference = calculateAngleDifference(heading, target_angle);
            degrees = command_buffer[command_index + 1];
            if (angle_difference < 20){
                motorAllStop();
                MoveMode = 4;
                delay(150);
                command_time = millis();
                correct_time = millis();
            }
            
            else{
                // delay to make sure motor actions are not being performed too quckly
                // to ensure data sent to motors is not corrupted
                updateMotorPositions(positions);
                MoveMode = 1;
            }

            return 0;
        
        // calculate movement target and start moving forward
        case 2 :
            centimeters = command_buffer[command_index + 2];
            command_time = millis();
            if (centimeters == 0){
                MoveMode = 0;
                return 1;
            }
            // calculate rotary encoder target based on motion constant
            rotaryTarget = (int) (MOTION_CONST * centimeters);
            
            restoreMotorPositions(positions);
            delay(50);
            testForward();
             
            MoveMode = 3;
            return 0;

        // perform movement
        case 3 :
            centimeters = command_buffer[command_index + 2];
            if ((millis() - command_time > 1500) && centimeters < 35){
                motorAllStop();
                restoreMotorPositions(positions);
                MoveMode = 0;
                return 1;
            }
            if (-1 * positions[MOTOR_LFT] < rotaryTarget && positions[MOTOR_RGT] < rotaryTarget){
                updateMotorPositions(positions);
                return 0;
            }
            else{
                motorAllStop();
                restoreMotorPositions(positions);
                MoveMode = 0;
                return 1;
            }

        // rotation correction
        case 4 :
            if (calculateAngleDifference(heading, target_angle) > 5){
                in_the_zone = 0;
                left_angle = calculateLeftAngle(heading, target_angle);
                right_angle = calculateRightAngle(heading, target_angle);
                if (left_angle < right_angle){
                    correctRight();
                }
                else {
                    correctLeft();
                }
            }
            else{
                motorAllStop();
                // exit if you've been in the zone enough time
                if (in_the_zone){
                    if (millis() - correct_time > ROTATION_CORRECT_TIME){
                        MoveMode = 2;
                        in_the_zone = 0;
                    }
                }
                else{
                    in_the_zone = 1;
                    correct_time = millis();
                }
          }
          return 0;
        default:
            return -1;
            break;       
    }
}
int holoMoveStep(){
    // Note that values are absolute, and differences are based on absolute magnetic heading
    int left_angle, right_angle, movement_angle, facing_angle;
    byte control_byte;
    float Rw = 0;
    
    movement_angle = command_buffer[command_index + 1];
    facing_angle = command_buffer[command_index + 2];
    control_byte = command_buffer[command_index] & byte(3);
    
    if (control_byte == byte(1)){
        movement_angle += 180;
    }
    else if (control_byte == byte(2)){
        facing_angle += 180;
    }
    else if (control_byte == byte(3)){
        movement_angle += 180;      
        facing_angle += 180;
    }
    // calculate movement direction
    movement_angle = movement_angle - (heading - 90);
    if (movement_angle < 0)
        movement_angle = 360 + movement_angle;

    if (movement_angle > 360)
        movement_angle = 360 - movement_angle;

    // calculate rotational direction
    if (calculateAngleDifference(heading, facing_angle) > 4){
        left_angle = calculateLeftAngle(heading, facing_angle);
        right_angle = calculateRightAngle(heading, facing_angle);
        if (left_angle < right_angle){
            Rw = -1 * (left_angle / 90.0);
        }
        else {
            Rw = right_angle / 90.0;
        }
    }
    else
        Rw = 0;
    
    holo_math(movement_angle, Rw);
    turn_holo_motors();
    delay(50);
    return 0;
    
}
void holo_math(int angle, float Rw){
        int rot_degrees;
        float rot_radians, vx, vy, m1_val, m2_val, m3_val, scale_factor;
        
        rot_degrees = (int) angle;
        rot_radians = rot_degrees * PI / 180;

        vx = cos(rot_radians);
        vy = sin(rot_radians);
            
        m1_val = -1 * sin(30  * PI / 180)  * vx + cos(30 * PI / 180)  * vy + Rw;
        m2_val = -1 * sin(150 * PI / 180) * vx + cos(150 * PI / 180) * vy  + Rw;
        m3_val = -1 * sin(270 * PI / 180) * vx + cos(270 * PI / 180) * vy  + Rw;
            
        scale_factor = fmax(abs(m1_val), abs(m2_val));
        scale_factor = 1 / fmax(scale_factor, abs(m3_val));
            
        //scale up to 1
        m1_val *= scale_factor;
        m2_val *= scale_factor;
        m3_val *= scale_factor;
                
        //scale up to 255
        m1_val *= POWER_RGT;
        m2_val *= POWER_LFT;
        m3_val *= POWER_BCK;
        
        holo_vals[0] = m2_val; // left
        holo_vals[1] = m1_val; // right
        holo_vals[2] = m3_val; // back
}


void turn_holo_motors(){
    if (holo_vals[0] > 0)
        motorForward(MOTOR_LFT, byte(holo_vals[0]));
    else
        motorBackward(MOTOR_LFT, byte(fabs(holo_vals[0])));
            
    if (holo_vals[1] > 0)
        motorForward(MOTOR_RGT, byte(holo_vals[1]));
    else
        motorBackward(MOTOR_RGT, byte(fabs(holo_vals[1])));
            
    if (holo_vals[2] > 0)
        motorForward(MOTOR_BCK, byte(holo_vals[2]));
    else
        motorBackward(MOTOR_BCK, byte(fabs(holo_vals[2])));    
}


int kickStep(){
    byte kick_val;
    switch(GrabMode){
        // initial state which starts ungrabbing
        case 0:
            command_time = millis();
            motorForward(GRABBER, GRABBER_POWER);
            GrabMode = 1;
            return 0;
        

        // if done with ungrabbing, start kicking
        case 1:
            if (millis() - command_time > GRAB_TIME){
                motorBackward(GRABBER, 0);
                motorForward(KICKER, (int) command_buffer[command_index + 1]);
                GrabMode = 2;
                command_time = millis(); // restore current time
            }
            return 0;
        

        // if done with kicking - start "un-kicking"
        case 2:
            if (millis() - command_time > KICK_TIME){
                motorBackward(KICKER, 189);
                GrabMode = 3;
                command_time = millis(); // restore current time
            }
            return 0;
        

        // if done with "un-kicking" - re-grab
        case 3:
            if (millis() - command_time > KICK_TIME){
                motorBackward(KICKER, 0);
                motorBackward(GRABBER, GRABBER_POWER);
                GrabMode = 4;
                command_time = millis(); // restore current time
            }
            return 0;
        

        // if re-grabbed, process is finished
        case 4:
            if (millis() - command_time > GRAB_TIME){
                motorBackward(GRABBER, 0);
                GrabMode = 0;
                return 1; // make sure that the only way to return from this function is to 
            }
            return 0;
        

        default:
            //Serial.writeln("BAD KICK");
            GrabMode = 0;
            return 1;
    }
    return -1;
}

int grabStep(){
    switch(GrabMode){
        case 0:
            motorBackward(GRABBER, GRABBER_POWER);
            command_time = millis();
            GrabMode = 1;
            return 0;
        case 1:
            if (millis() - command_time > GRAB_TIME){
                motorBackward(GRABBER, 0);
                GrabMode = 0;
                finishGrabbing = 0;
                GrabberStatus = 0;
                return 1;
            }
            return 0;
    }
}

int unGrabStep(){
    switch(GrabMode){
        case 0:
            motorForward(GRABBER, GRABBER_POWER);
            command_time = millis();
            GrabMode = 1;
            return 0;
        case 1:
            if (millis() - command_time > GRAB_TIME){
                motorForward(GRABBER, 0);
                GrabMode = 0;
                GrabberStatus = 1;
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
        mag[2] += MAG_OFFSET_Z;

        // angle between X and north
        heading = Lsm303d.getHeading(mag);
        
        // tilt-compensated angle
        titleHeading = Lsm303d.getTiltHeading(mag, realAccel);
        }
}


void calibrateCompass(){
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

        // angle between X and north
        // heading = Lsm303d.getHeading(mag);
        // tilt-compensated angle
        // titleHeading = Lsm303d.getTiltHeading(mag, realAccel);
        }
        
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
  if (mag[2] > mag_max_z){
      mag_max_z = mag[2];
  }
  if (mag[2] < mag_min_z){
      mag_min_z = mag[2];
  }
  /* Outdated  calibration procedure. Useful for debugging
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
    Serial.print("MIN Z: ");
    Serial.println(mag_min_z);
    Serial.print("MAX Z: ");
    Serial.println(mag_max_z);
    
    Serial.print("BIAS_X: ");
    Serial.println(-0.5 * (mag_max_x + mag_min_x));
    Serial.print("BIAS_Y: ");
    Serial.println(-0.5 * (mag_max_y + mag_min_y));
    Serial.print("BIAS_Z: ");
    Serial.println(-0.5 * (mag_max_z + mag_min_z));
 }*/
 MAG_OFFSET_X = int(-0.5 * (mag_max_x + mag_min_x));
 MAG_OFFSET_Y = int(-0.5 * (mag_max_y + mag_min_y));
 MAG_OFFSET_Z = int(-0.5 * (mag_max_z + mag_min_z));
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