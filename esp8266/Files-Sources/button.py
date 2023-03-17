from machine import Pin
import time
import utils 

_ON = 0
_OFF = 1
_MIN_DIFF = 100
_LONG_PRESS = 3000

class Button:
    def __init__(self, pinNumber, callbackOnPressedShort, callbackOnPressedLong):
        global _ON, _OFF
        self.callbackOnPressedShort = callbackOnPressedShort
        self.callbackOnPressedLong = callbackOnPressedLong
        self.pin = Pin(pinNumber, Pin.IN, Pin.PULL_UP)
        self.lastPressed = time.ticks_ms()
        self.old_state = _OFF
        self.start_press = time.ticks_ms()
        
    def update(self):
        global _ON, _OFF, _MIN_DIFF, _LONG_PRESS
        new_state = self.pin.value()
        if(new_state != self.old_state):
            current = time.ticks_ms()
            if (current < self.lastPressed):
                self.lastPressed = current
            diff = current - self.lastPressed
            if(diff > _MIN_DIFF):
                self.lastPressed = time.ticks_ms()
                if (self.old_state == _OFF and new_state == _ON):
                    self.start_press = time.ticks_ms()
                elif (self.old_state == _ON and new_state == _OFF):
                    if(current < self.start_press):
                        self.start_press = current
                    diff_press = current - self.start_press
                    if(diff_press > _LONG_PRESS):
                        self.btn_pressed_long()
                    else:
                        self.btn_pressed_short()
                if(new_state != self.old_state):
                    self.old_state = new_state
    
    def btn_pressed_short(self):
        try:
            utils.trace("Button : pressed short")
            if self.callbackOnPressedShort is not None:
                self.callbackOnPressedShort()
        except Exception:
            pass

    def btn_pressed_long(self):
        try:
            utils.trace("Button : pressed long")
            if self.callbackOnPressedLong is not None:
                self.callbackOnPressedLong()
        except Exception:
            pass