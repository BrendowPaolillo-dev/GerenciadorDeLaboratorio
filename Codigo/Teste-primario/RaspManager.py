"""
Codigo de leitura das portas dos Arduinos
Escrita de dados em arquivos
Envio de dados para a plataforma Cayenne
"""
import cayenne.client
import time
import credentials
import serial
from datetime import datetime

credentials = credentials.Credentials()
MQTT_USERNAME  = credentials.username
MQTT_PASSWORD  = credentials.password
MQTT_CLIENT_ID = credentials.clientID

nowTime = datetime.now()
date = nowTime.strftime("%m/%d/%Y")
serialPort = serial.Serial ('/dev/ttyACM0', 9600)
serialPort1 = serial.Serial ('/dev/ttyACM1', 9600)

currFile = open("current.txt", "w+")
powerFile = open("power.txt", "w+")
consumeFile = open ("consume.txt", "w+")

currFile.write(nowTime.strftime("%m/%d/%Y, %H:%M:%S") + "\n")
powerFile.write(nowTime.strftime("%m/%d/%Y, %H:%M:%S") + "\n")
consumeFile.write(nowTime.strftime("%m/%d/%Y, %H:%M:%S") + "\n")

currFile.close()
powerFile.close()
consumeFile.close()
consume = 0

def on_message(message):
  print("message received: " + str(message))
  # If there is an error processing the message return an error string, otherwise return nothing.

client = cayenne.client.CayenneMQTTClient()
client.on_message = on_message
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID)
# For a secure connection use port 8883 when calling client.begin:
# client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, port=8883)

timestamp = 0

while True:
  nowTime = datetime.now()
  
  if ((currFile.closed == True) and (powerFile.closed == True) and (consumeFile.closed == True)):
      currFile = open("current.txt", "a")
      powerFile = open("power.txt", "a")
      consumeFile = open("consume.txt", "a")
  
  if (date != nowTime.strftime("%m/%d/%Y")):
      date = nowTime.strftime("%m/%d/%Y")
      currFile.write(nowTime.strftime("%m/%d/%Y, %H:%M:%S") + "\n")
      powerFile.write(nowTime.strftime("%m/%d/%Y, %H:%M:%S") + "\n")
         
  current = serialPort.readline()
  power = serialPort.readline()
  light = float(serialPort1.readline())
  consume = (((float(current)/60)/24)/30) + consume
  print (current)
  print (power)
  print ("consumo", consume)
  
  currFile.write(str(float(current))+ "\n")
  powerFile.write(str(float(power))+ "\n")
  consumeFile.write(str(float(consume))+ "\n")
  
  currFile.close()
  powerFile.close()
  consumeFile.close()

  client.loop()

  if (time.time() > timestamp + 10):
    client.luxWrite(2, light)
    client.virtualWrite(4, float(current), "current", "a")
    client.virtualWrite(5, float(power), "pow", "w")