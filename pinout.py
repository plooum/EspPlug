from machine import Pin

class PinOut:
    def __init__(self, num):
        self.pinOut = Pin(num, Pin.OUT)
    def setValue(self,val):
        self.pinOut.value(val)
    def on(self):
        self.setValue(1)
    def off(self):
        self.setValue(0)
    def getValue(self):
        return (self.pinOut.value()>0) 