int pinoSensorLuz = A0;

void setup(){
  Serial.begin(9600);
}
void loop(){
  int valorLuz = analogRead(pinoSensorLuz);
  Serial.println(valorLuz);
  delay(30000);
}
