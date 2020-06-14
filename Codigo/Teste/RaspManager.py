import serial
from datetime import datetime

nowTime = datetime.now()
date = nowTime.strftime("%m/%d/%Y")
serialPort = serial.Serial ('/dev/ttyACM0', 9600)

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

while 1 :
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