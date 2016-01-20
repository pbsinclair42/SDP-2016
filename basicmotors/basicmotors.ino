#include "SDPArduino.h"
#include "Arduino.h"
#include <Wire.h>

int blink_pin = 13;
int a = 5;
int b = 10;
int c = 20;
void setup()
{
   motorForward(0, 0);
   motorForward(1, 0);
   motorForward(2, 0);
   motorForward(3, 0);
   motorForward(4, 0);
   motorForward(5, 0); 
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
   while(Serial.available() > 0)
   {
        serial_in_char = (char) Serial.read();
        Serial.print(serial_in_char);
        
        if (serial_in_char == 'f'){//forward
            motorForward(1, 100);
            motorForward(3, 100);
            motorForward(0, 0);
            motorForward(2, 0);
        } else if (serial_in_char == 'b'){//backwards
            motorBackward(1, 100);
            motorBackward(3, 100);
            motorForward(0, 0);
            motorForward(2, 0);
        } else if (serial_in_char == 'l'){//left
            motorForward(1, 0);
            motorForward(3, 0);
            motorBackward(0, 100);
            motorBackward(2, 100);
        } else if (serial_in_char == 'r'){//right
            motorForward(1, 0);
            motorForward(3, 0);
            motorForward(0, 100);
            motorForward(2, 100);
        } else if (serial_in_char == 's'){//stop
            motorStop();
        } else if (serial_in_char == 'd'){//diagonallift
            motorForward(1, 0);
            motorForward(3, 0);
            motorForward(0, 100);
            motorForward(2, 100);
        } else if (serial_in_char == 'e'){//diagonal right
            motorForward(1, 0);
            motorForward(3, 0);
            motorForward(0, 100);
            motorForward(2, 100);
        } else if (serial_in_char == 'o'){//rotate left
            motorForward(1, 0);
            motorForward(3, 0);
            motorForward(0, 100);
            motorForward(2, 100);
        } else if (serial_in_char == 'p'){//rotate right
            motorForward(1, 0);
            motorForward(3, 0);
            motorForward(0, 100);
            motorForward(2, 100);
        } else  { //error 
            Serial.print("What should I do?!");
        }

   } 
 motorStop();
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
