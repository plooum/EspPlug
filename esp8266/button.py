from machine import Pin
import time
import utils 

class Button:
    def __init__(self, pinNumber, callbackOnPressed):
        self.pinNumber = pinNumber 
        self.callbackOnPressed = callbackOnPressed
        self.pin = Pin(self.pinNumber, Pin.IN, Pin.PULL_UP)
        self.pin.irq(trigger = Pin.IRQ_FALLING, handler = self.btn_pressed)
        self.lastExec = 0

    def btn_pressed(self, irq):
        curMs = time.ticks_ms()
        if curMs < self.lastExec:
            self.lastExec = 0
        if curMs - self.lastExec > 500:
            self.lastExec = curMs
            self.btn_pressed_filtered()

    def btn_pressed_filtered(self):
        try:
            utils.trace("Button : pressed")
            if self.callbackOnPressed is not None:
                self.callbackOnPressed()
        except Exception as e:
            utils.trace("Button : Error, " + str(e))
