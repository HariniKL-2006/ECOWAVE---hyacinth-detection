#include <Arduino.h>
// Prototype scaffold only. Adapt pins and motor control to actual hardware.
// NEVER connect motors directly to GPIO. Use rated ESCs/drivers and physical E-stop.
constexpr int PROP_PIN=25, CUTTER_ENABLE_PIN=26, TRIG_PIN=5, ECHO_PIN=18, ESTOP_PIN=27;
constexpr int PWM_CHANNEL=0, PWM_FREQ=1000, PWM_BITS=8;
constexpr int OBSTACLE_STOP_CM=50;

float distanceCm() {
  digitalWrite(TRIG_PIN, LOW); delayMicroseconds(3);
  digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10); digitalWrite(TRIG_PIN, LOW);
  unsigned long t=pulseIn(ECHO_PIN, HIGH, 25000UL);
  return t ? (t*0.0343f)/2.0f : -1.0f;
}
void stopAll() { ledcWrite(PWM_CHANNEL,0); digitalWrite(CUTTER_ENABLE_PIN,LOW); }
void setup() {
  Serial.begin(115200); pinMode(TRIG_PIN,OUTPUT); pinMode(ECHO_PIN,INPUT);
  pinMode(CUTTER_ENABLE_PIN,OUTPUT); pinMode(ESTOP_PIN,INPUT_PULLUP);
  ledcSetup(PWM_CHANNEL,PWM_FREQ,PWM_BITS); ledcAttachPin(PROP_PIN,PWM_CHANNEL); stopAll();
  Serial.println("EcoWave ready; outputs stopped. Commands: STOP, MOVE <0-255>, CUTTER ON, CUTTER OFF");
}
void loop() {
  float d=distanceCm();
  bool blocked=(d>0 && d<OBSTACLE_STOP_CM);
  if (digitalRead(ESTOP_PIN)==LOW || blocked) { stopAll(); if(blocked) Serial.println("OBSTACLE_STOP"); }
  if (Serial.available()) {
    String s=Serial.readStringUntil('\n'); s.trim(); s.toUpperCase();
    if(s=="STOP") { stopAll(); Serial.println("OK STOPPED"); }
    else if(s.startsWith("MOVE ")) {
      int v=constrain(s.substring(5).toInt(),0,255);
      if(!blocked && digitalRead(ESTOP_PIN)!=LOW) { ledcWrite(PWM_CHANNEL,v); Serial.printf("OK MOVE %d\n",v); }
      else { stopAll(); Serial.println("BLOCKED"); }
    } else if(s=="CUTTER OFF") { digitalWrite(CUTTER_ENABLE_PIN,LOW); Serial.println("OK CUTTER OFF"); }
    else if(s=="CUTTER ON" && !blocked && digitalRead(ESTOP_PIN)!=LOW) {
      digitalWrite(CUTTER_ENABLE_PIN,HIGH); Serial.println("WARNING: cutter enabled; verify physical safety");
    } else Serial.println("ERR command blocked or unknown");
  }
  delay(50);
}
