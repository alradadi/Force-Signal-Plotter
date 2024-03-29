from src.Input.fakeSerial import Serial
from collections import deque
from PyQt5.QtCore import pyqtSignal, QObject
import time



## inheriting from QObject allows the class to emit signals that indicate model has started collecting data
class Signal(QObject):
    startedCollecting = pyqtSignal()
    finishedCollecting = pyqtSignal()
    resetPort = pyqtSignal()


# class is static so that the table and graph classes have access to the same data
class Data():
    # bufferSize = 500
    ## deque(iterable, maxlen)
    graphDataBuffer = deque()  # using deque becuase appending and removing performace is O(1) comparaed to lists performance O(n)
    tableDataBuffer = deque()
    signal = Signal()

    @classmethod
    def startCollecting(klass):
        Serial.start()  ## opens up a fake serial port and starts writing random data to it (#port only collects for 10 seconds)
        time.sleep(1 / 100)  ## give time for the port to start up befre emmiting the sginal
        klass.signal.startedCollecting.emit()  ## emit signal to indicate that model started collecting data

    @classmethod
    def updateBuffers(klass):
        if (Serial.isOpen):
            data = Serial.readline()
            if (len(klass.graphDataBuffer) % 4 == 0):
                klass.addToBuf(klass.tableDataBuffer, data, True)
            klass.addToBuf(klass.graphDataBuffer, data, False)
        else:
            klass.signal.finishedCollecting.emit() ## emit signal so that the graph class knows when to stop plotting
            print(Data.graphDataBuffer)
            print(Data.tableDataBuffer)


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
        Serial.close()
        klass.signal.resetPort.emit()

