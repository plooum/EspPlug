from machine import Pin
import time
import utils 

ON = 0
OFF = 1
MIN_DIFF = 100
LONG_PRESS = 2000
class Button:
    def __init__(self, pinNumber, callbackOnPressedShort, callbackOnPressedLong):
        global ON, OFF
        self.callbackOnPressedShort = callbackOnPressedShort
        self.callbackOnPressedLong = callbackOnPressedLong
        self.pin = Pin(pinNumber, Pin.IN, Pin.PULL_UP)
#         self.pin.irq(trigger = Pin.IRQ_FALLING | Pin.IRQ_RISING, handler = self.btn_pressed)
#         self.lastExec = 0
        self.lastPressed = time.ticks_ms()
        self.old_state = OFF
        self.start_press = time.ticks_ms()
        
    def update(self):
        global ON, OFF, MIN_DIFF, LONG_PRESS
        new_state = self.pin.value()
        if(new_state != self.old_state):
            current = time.ticks_ms()
            if (current < self.lastPressed):
                self.lastPressed = current
            diff = current - self.lastPressed
            if(diff > MIN_DIFF):
                if (self.old_state == OFF and new_state == ON):
                    self.start_press = time.ticks_ms()
                elif (self.old_state == ON and new_state == OFF):
                    if(current < self.start_press):
                        self.start_press = current
                    diff_press = current - self.start_press
                    if(diff_press > LONG_PRESS):
                        self.btn_pressed_long()
                    else:
                        self.btn_pressed_short()
                if(new_state != self.old_state):
                    self.old_state = new_state
    
#     def btn_pressed(self):
#         curMs = time.ticks_ms()
#         if(self.pin.value() == 0):
#             self.lastPressed = curMs
#         else:
#             if (curMs < self.lastExec):
#                 self.lastExec = 0
#             difExec = curMs - self.lastExec
#             if (difExec > 500):
#                 self.lastExec = curMs
#                 difPressed = curMs - self.lastPressed
#                 if (difPressed > 5000):
#                     self.btn_pressed_long()
#                 else:
#                     self.btn_pressed_short()
    
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