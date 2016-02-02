#include <Wire.h>
#include "SDPArduino.h"
void setup() {
  SDPsetup();
  loop();
}
void loop() {
  helloWorld();
  while (!Serial.find("TEST"));
  Serial.println("Message received!");
}
