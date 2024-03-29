#from src.Input.fakeSerial import Serial
from collections import deque
from PyQt5.QtCore import pyqtSignal, QObject
import time
import csv
import serial



## inheriting from QObject allows the class to emit signals that indicate model has started collecting data
class Signal(QObject):
    startedCollecting = pyqtSignal()
    resetTable = pyqtSignal()
    loadData = pyqtSignal()


# class is static so that the table and graph classes have access to the same data
class Data():
    # bufferSize = 500
    ## deque(iterable, maxlen)
    graphDataBuffer = deque()  # using deque becuase appending and removing performace is O(1) comparaed to lists performance O(n)
    tableDataBuffer = deque()
    timeBuffer = deque()
    signal = Signal()
    serial1 = serial.Serial('COM4', baudrate=9600, timeout=100)
    timeStep = 0

    @classmethod
    def startCollecting(klass):
        if(not klass.serial1.isOpen()):
            klass.serial1.open()
        klass.serial1.flushInput()
        #klass.serial1 = serial.Serial('COM4', baudrate=9600, timeout=None)
        #klass.Serial.start()  ## opens up a fake serial port and starts writing random data to it (#port only collects for 10 seconds)
        #time.sleep(1 / 100)  ## give time for the port to start up befre emmiting the sginal
        klass.signal.startedCollecting.emit()  ## emit signal to indicate that model started collecting data

    @classmethod
    def updateBuffers(klass):
        #print (bytes.decode(klass.serial1.readline()))
        if (klass.serial1.isOpen()):
            temp = bytes.decode(klass.serial1.readline())
            temp = temp.replace("\n", "")
            temp = temp.replace("\r", "")
            data = float(temp)
            if (len(klass.graphDataBuffer) % 4 == 0):
                klass.addToBuf(klass.tableDataBuffer, data, True)
                klass.addToBuf(klass.timeBuffer, klass.timeStep, True)
            klass.timeStep += 0.03
            klass.addToBuf(klass.graphDataBuffer, data, False)
        else:
            klass.signal.finishedCollecting.emit() ## emit signal so that the graph class knows when to stop plotting
            print(Data.graphDataBuffer)
            print(Data.tableDataBuffer)
            klass.saveData()

    @classmethod
    def closePort(klass):
        klass.serial1.close()
        klass.saveData()

    # add plot points to buffer.
    # appends left for the graph buffer and right for the table buffer
    @classmethod
    def addToBuf(klass, buf, val, isAppendRight):
        if(isAppendRight):
            buf.append(val)
        else:
            buf.appendleft(val)


    @classmethod
    def reset(klass):
        klass.graphDataBuffer.clear()
        klass.tableDataBuffer.clear()
        #klass.serial1.close()
        klass.signal.resetTable.emit()

    @classmethod
    def saveData(klass):
        #now =time.strftime("%a %b %d %H.%m %y")
        #with open(("Force Recording At "+now +".csv"), 'w') as forceFile:  //Comment out next line and uncomment previous ones for current time save
        with open("force.csv", 'w') as forceFile:
            forceWriter = csv.writer(forceFile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for eachEntry in list(klass.tableDataBuffer):
                forceWriter.writerow([eachEntry])
