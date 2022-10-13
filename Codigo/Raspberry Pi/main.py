import serial
import datetime
import pandas as pd
from time import sleep

class CSVGenerator:
    def __init__(self):
        self.fileName = "./collectedData/LabManager_PowerConsumption_" + datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S') + ".csv"
        self.colNames = ["current (A)","timestamp"]

    def insertIntoCsv(self, value):
        df = pd.DataFrame ({
          self.colNames[0]: value,
          self.colNames[1]:  datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S'),
          })
        with open(self.fileName, 'a') as f:
          df.to_csv(f, header=f.tell()==0, index=False)


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


class Relay:
    def __init__(self):
        self.curr = False
        self.timer = datetime.datetime.now()
        self.lastTimer = datetime.datetime.now()
        self.toTurnOff = datetime.datetime.now()
        self.permanencyTime = datetime.timedelta(seconds=15)
        self.countDownTime = datetime.timedelta(seconds=1)

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
        sleep(0.1)
        self.ser.reset_input_buffer()

    def getMessage(self):
        if self.ser.isOpen():
            try:
                while self.ser.inWaiting() == 0:
                    pass
                if self.ser.inWaiting() > 0:
                    answer = str(self.ser.readline().decode("utf-8").rstrip())
                    self.ser.flushInput()
                    return answer
            except KeyboardInterrupt:
                pass

    def sendMessage(self, key="", data=""):
        self.ser.write(key.encode("utf-8")+ b"," + data.encode("utf-8") + b"\n")
        self.ser.flushInput()



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

    def requestSerial(self):
        return self.com.getMessage().split(": ")

    def setTimer(self):
        self.timer = datetime.datetime.now()

    def setLastTimer(self):
        self.lastTimer = datetime.datetime.now()

    def hasPassedRequestTime(self):
        return self.timer - self.lastTimer >= self.requestTime

    def run(self):
        if self.needRequest:
            serialResponse = self.requestSerial()

            print(serialResponse)

            if serialResponse[0] == "PIR":
                if serialResponse[1] == "True":
                    if not self.pir.lastDetectedIsInPermanency:
                        self.pir.setDetected()
                        self.pir.setDetectedInterval()
                        self.relay.turnOn(self.com)
                        self.relay.setTimer()
                        self.relay.setLastTimer()
                        self.needRequest = False
                        print("Liguei tudo")

                elif serialResponse[1] == "False":
                    self.pir.setMiss()

                    if self.relay.toTurnOff <= self.timer:
                        self.relay.turnOff(self.com)
                        self.needRequest = False
                        print("Desliguei tudo")

            self.setLastTimer()

        else:
            if self.relay.hasPassedPermanencyTime() and self.relay.curr:
                self.relay.toTurnOff = self.relay.timer + self.relay.countDownTime
                print("Se prepara que eu quero desligar")
                self.pir.setMissInterval()
                self.needRequest = True

        if self.hasPassedRequestTime() and not self.relay.curr:
            print("Vou lançar a requisição")
            self.needRequest = True

        if self.curr.hasReadCurrTime():
            self.curr.getCurr(self.com)
            serialResponse = self.requestSerial()
            if serialResponse[0] == "Curr":
                print("Vou coletar a corrente")
                self.curr.setLastTimer()
                self.csvGen.insertIntoCsv([serialResponse[1]])

        self.curr.setTimer()
        self.relay.setTimer()
        self.setTimer()


def main():
    man = Manager()

    while True:
        man.run()


if __name__ == "__main__":
    main()
