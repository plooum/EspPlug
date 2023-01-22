from machine import Pin
import time
import utils 

class Button:
    def __init__(self, pinNumber, callbackOnPressedShort, callbackOnPressedLong):
        self.pinNumber = pinNumber 
        self.callbackOnPressedShort = callbackOnPressedShort
        self.callbackOnPressedLong = callbackOnPressedLong
        self.pin = Pin(self.pinNumber, Pin.IN, Pin.PULL_UP)
        self.pin.irq(trigger = Pin.IRQ_FALLING | Pin.IRQ_RISING, handler = self.btn_pressed)
        self.lastExec = 0
        self.lastPressed = time.ticks_ms()
    
    def btn_pressed(self, irq):
        curMs = time.ticks_ms()
        if(self.pin.value() == 0):
            self.lastPressed = curMs
        else:
            if (curMs < self.lastExec):
                self.lastExec = 0
            difExec = curMs - self.lastExec
            if (difExec > 500):
                self.lastExec = curMs
                difPressed = curMs - self.lastPressed
                if (difPressed > 5000):
                    self.btn_pressed_long()
                else:
                    self.btn_pressed_short()
    
    def btn_pressed_short(self):
        try:
            utils.trace("Button : pressed short")
            if self.callbackOnPressedShort is not None:
                self.callbackOnPressedShort()
        except Exception as e:
            utils.trace("Button : Error pressed short, " + str(e))

    def btn_pressed_long(self):
        try:
            utils.trace("Button : pressed long")
            if self.callbackOnPressedLong is not None:
                self.callbackOnPressedLong()
        except Exception as e:
            utils.trace("Button : Error pressed long, " + str(e))