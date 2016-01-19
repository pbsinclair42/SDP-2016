#include "SDPArduino.h"
#include "Arduino.h"
#include <Wire.h>


/*

motor layout

    1
3       4
    2

*/

int blink_pin = 13;
int a = 5;
int b = 10;
int c = 20;
void setup()
{/*
   motorForward(0, 0);
   motorForward(1, 0);
   motorForward(2, 0);
   motorForward(3, 0);
   motorForward(4, 0);
   motorForward(5, 0); 
   */
   pinMode(blink_pin, OUTPUT);
   SDPsetup();

}

void motorStop()
{
 motorForward(0, 0);
 motorForward(1, 0);
 motorForward(2, 0);
 motorForward(3, 0);
 motorForward(4, 0);
 motorForward(5, 0); 
}

char serial_in_char;
void loop()
{
  motorForward(0, 100);
  motorForward(1, 100);
  motorForward(2, 100);
  motorForward(3, 100);
  motorForward(4, 100);
  motorForward(5, 100);
  helloWorld();
  delay(1000);
  /*
   while(Serial.available() > 0)
   {
        serial_in_char = (char) Serial.read();
        Serial.print(serial_in_char);
        
        if (serial_in_char == 'f'){//forward
            motorForward(2, 100);
            motorForward(3, 100);
            motorForward(0, 0);
            motorForward(1, 0);
        } else if (serial_in_char == 'b'){//backwards
            motorBackward(2, 100);
            motorBackward(3, 100);
            motorForward(0, 0);
            motorForward(1, 0);
        }
        else if (serial_in_char == 'l'){//right
            motorForward(2, 0);
            motorForward(3, 0);
            motorBackward(0, 100);
            motorForward(1, 100);
        }
        else if (serial_in_char == 'r'){//left
            motorForward(2, 0);
            motorForward(3, 0);
            motorForward(0, 100);
            motorBackward(1, 100);
        } else if (serial_in_char == 's'){//stop
            motorStop();
        }else if (serial_in_char == 'd'){//diagonalleft <- test
            motorForward(1, 100);
            motorForward(2, 0);
            motorForward(3, 100);
            motorBackward(0, 100);
        }else if (serial_in_char == 'e'){//diagonal right <- test
            motorBackward(1, 50);
            motorForward(3, 0);
            motorForward(0, 100);
            motorForward(2, 100);
        }else if (serial_in_char == 'o'){//rotate left <- test
            motorBackward(0, 100);
            motorForward(3, 0);
            motorForward(1, 0);
            motorForward(2, 0);
        }else if (serial_in_char == 'p'){//rotate right <-test
            motorForward(0, 100);
            motorForward(2, 100);
            motorForward(0, 0);
            motorForward(2, 0);
        }
   } 
  */
 /*
 motorForward(0, 100);
 motorForward(1, 100);
 motorBackward(2, 100);
 digitalWrite( blink_pin, HIGH);
 delay(5000);
 motorForward(0, 0);
 motorForward(1, 0);
 motorBackward(2, 0);
 delay(5000);*/
}
