//Código de leitura do amperimetro e calculo de potencia

#include "EmonLib.h"

EnergyMonitor emon1;

//Porta ligada ao pino
int porta_rele = 7;
int sensor_luz = A0;
int valor_luz = 0;

int rede = 127;
int pino_sct = A1;
  
void setup()
{
  //Define pinos para o rele como saida
  Serial.begin(9600);
  pinMode(porta_rele, OUTPUT); 
  emon1.current(pino_sct, 60);
}
   
void loop()
{
  //Calcula a corrente
  double Irms = emon1.calcIrms(1480);
  //Mostra o valor da corrente no serial monitor e display
  Serial.println(Irms); // Irms
  
  double pot = Irms * (double)rede;
  Serial.println(pot); // Irms
  
  
  valor_luz = analogRead(sensor_luz);
  if (valor_luz < 450){
    digitalWrite(porta_rele, LOW);  //Liga rele 1
  }else if (valor_luz < 20){
    digitalWrite(porta_rele, HIGH); //Desliga rele 1
  }else {
    digitalWrite(porta_rele, HIGH); //Desliga rele 1
  }
  delay(30000);
}
