#include "EmonLib.h"

EnergyMonitor emon1;


int pirPin = 2;                 // PIR In pin
int relayPin = 7;               // Relay Out pin
int ampmeterPin = A1;           // Amperemeter In pin

int pirStat = "";                // PIR status
String key = "";
String data = "";

void sendData(String key, String data){
  Serial.println(key + ": " + data);
  delay(10);
}

void sendCurrData(){
  double data = emon1.calcIrms(1480);
  sendData("Curr", String(data,2));
}

void receiveData(){
  key = "";
  data = "";
  if (Serial.available()) {
    delay(10);
    while (Serial.available() > 0) {
      key = Serial.readStringUntil(',');
      data = Serial.readStringUntil('\n');
    }
    Serial.flush();
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(pirPin, INPUT);
  pinMode(relayPin, OUTPUT);
  emon1.current(ampmeterPin, 60);
}

void loop() {
  if (key =="curr"){
    sendCurrData();
  } else if (key == "relay") {
    if (data == "HIGH"){
      digitalWrite(relayPin, HIGH); //LIGA
    }else {
      digitalWrite(relayPin, LOW); //DESLIGA
    }
  } else if (key == "pir"){
    pirStat = digitalRead(pirPin);
    if (pirStat == HIGH) {
      sendData("PIR", "True");
    } else {
      sendData("PIR", "False");
    }
  }

  receiveData();
  delay(500);
}
