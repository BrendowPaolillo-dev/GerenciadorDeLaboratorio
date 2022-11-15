import serial
import datetime
import pandas as pd
from time import sleep

import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("Lab Manager")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('log.txt', backupCount=1, maxBytes=2 ** 20)
logger.addHandler(handler)


def now():
    return datetime.datetime.now()


def now_str():
    return now().strftime('%Y-%m-%d_%H:%M:%S')


def log(text):
    logger.info(now_str() + ": " + text)


class CSVGenerator:
    def __init__(self):
        self.fileName = "/home/LabManager/Documents/TCC/RaspberryPi/collectedData/LabManager_PowerConsumption_" + now_str()  + ".csv"
        self.colNames = ["current (A)","timestamp"]

    def insertIntoCsv(self, value):
        df = pd.DataFrame ({
          self.colNames[0]: value,
          self.colNames[1]: now_str(),
        })
        with open(self.fileName, 'a') as f:
          df.to_csv(f, header=f.tell()==0, index=False)
          f.close()


class CurrentSensor:
    def __init__(self):
        self.timer = datetime.datetime.now()
        self.lastTimer = datetime.datetime.now()
        self.readCurrTime = datetime.timedelta(seconds=5)

    def getCurr(self, com):
        com.sendMessage("curr")

    def setTimer(self):
        self.timer = datetime.datetime.now()

    def setLastTimer(self):
        self.lastTimer = datetime.datetime.now()

    def hasReadCurrTime(self):
        return self.timer - self.lastTimer >= self.readCurrTime


class PIRSensor:
    def __init__(self):
        self.detected = False
        self.lastDetectedIsInPermanency = False

    def setDetected(self):
        self.detected = True

    def setMiss(self):
        self.detected = False

    def setDetectedInterval(self):
        self.lastDetectedIsInPermanency = True

    def setMissInterval(self):
        self.lastDetectedIsInPermanency = False
    
    def getPir(self, com):
        com.sendMessage("pir")


class Relay:
    def __init__(self):
        self.curr = False
        self.timer = datetime.datetime.now()
        self.lastTimer = datetime.datetime.now()
        self.toTurnOff = datetime.datetime.now()
        self.permanencyTime = datetime.timedelta(minutes=5)
        self.countDownTime = datetime.timedelta(seconds=5)

    def turnOn(self, com):
        self.curr = True
        com.sendMessage("relay", "HIGH")


    def turnOff(self, com):
        self.curr = False
        com.sendMessage("relay", "LOW")


    def hasPassedPermanencyTime(self):
        return self.timer - self.lastTimer >= self.permanencyTime

    def setTimer(self):
        self.timer = datetime.datetime.now()

    def setLastTimer(self):
        self.lastTimer = datetime.datetime.now()


class Comunicator:
    def __init__(self):
        self.ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
        self.ser.reset_input_buffer()

    def getMessage(self):
        sleep(0.25)
        if self.ser.isOpen():
            try:
                if self.ser.inWaiting() > 0:
                    answer = str(self.ser.readline().decode("utf-8").rstrip())
                    self.ser.flushInput()
                    return answer
            except KeyboardInterrupt:
                pass
        return ''

    def sendMessage(self, key="", data=""):
        self.ser.write(key.encode("utf-8")+ b"," + data.encode("utf-8") + b"\n")
        sleep(1)


class Manager:
    def __init__(self):
        self.timer = datetime.datetime.now()
        self.lastTimer = datetime.datetime.now()
        self.requestTime = datetime.timedelta(seconds=10)

        self.com = Comunicator()
        self.pir = PIRSensor()
        self.relay = Relay()
        self.curr = CurrentSensor()
        self.csvGen = CSVGenerator()

        self.needRequest = True

        # Variável para evitar leitura suja do sensor de presença inicial
        self.count = 0

    def requestSerial(self):
        return self.com.getMessage().split(": ")

    def setTimer(self):
        self.timer = datetime.datetime.now()

    def setLastTimer(self):
        self.lastTimer = datetime.datetime.now()

    def hasPassedRequestTime(self):
        return self.timer - self.lastTimer >= self.requestTime

    def run(self):
        serialResponse = self.requestSerial()

        if serialResponse[0] != "":
            if serialResponse[0] == "PIR":
                if serialResponse[1] == "True":
                    log("Movimento detectado")
                    self.pir.setDetected()
                    self.relay.setLastTimer()

                    if self.count > 3:
                        self.relay.turnOn(self.com)
                    else:
                        self.count += 1
                elif serialResponse[1] == "False":
                    log("Nenhum movimento detectado")
                    self.pir.setMiss()
                    if self.relay.hasPassedPermanencyTime():
                        log("Desliguei as luzes")
                        self.relay.turnOff(self.com)
                        self.relay.setLastTimer()
                self.setLastTimer()

            elif serialResponse[0] == "Curr":
                log("Armazenando a corrente")
                self.curr.setLastTimer()
                self.csvGen.insertIntoCsv([serialResponse[1]])

        if self.hasPassedRequestTime():
            log("Detectando movimentos")
            self.pir.getPir(self.com)

        if self.curr.hasReadCurrTime():
            log("Pedindo o valor da corrente")
            self.curr.getCurr(self.com)

        self.curr.setTimer()
        self.relay.setTimer()
        self.setTimer()

def main():
    man = Manager()

    while True:
        man.run()

if __name__ == "__main__":
    main()
