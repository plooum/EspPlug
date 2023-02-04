import esp
import gc
from time import time
import config
import collections

class UTILS:
    @staticmethod
    def init():
        esp.osdebug(None)
        gc.collect()
    @staticmethod
    def freeMemory():
        gc.collect()

class CIPHER:
    @staticmethod
    def enc(msg):
        ret=msg
#         ret = ""
#         i=0
#         while i < len(msg):
#             ret += chr(ord(msg[i])+10)
#             i+=1
        return ret
    @staticmethod
    def dec(msg):
        ret=msg
#         ret = ""
#         i=0
#         while i < len(msg):
#             ret += chr(ord(msg[i])-10)
#             i+=1
        return ret
    
def trace(msg):
    if(config.getValue(config._debug)):
        print(str(time()) +" : "+ msg)

class Command:
    def __init__(self, identifier, description, target, configKey, takeParameters, takeCallback):
        self.takeCallback = takeCallback
        self.identifier = identifier
        self.description = description
        self.target = target
        self.configKey = configKey
        self.takeParameters = takeParameters
    
    def executeCallback(self, callback):
        if(self.target is not None):
            trace("Command : executing, " + self.identifier)
            self.target(callback)
            
    def execute(self, arg = None):
        if(self.target is not None):
            if(arg is None):
                trace("Command : executing, " + self.identifier)
                if self.takeParameters:
                    return self.target("")
                else:
                    return self.target()
            else:
                trace("Command : executing, " + self.identifier + ", arg = " + str(arg))
                return self.target(arg)
        return None
                
class Commands:
    def __init__(self):
        self.commands = {}
    
    def add(self,identifier, description, target, configKey= "", takeParameters = False, takeCallback = False):
        self.commands[identifier] = Command(identifier, description, target, configKey, takeParameters, takeCallback)
        
    def execute(self,identifier, arg = None):
        if identifier in commands.keys():
            self.commands[identifier].execute(arg)

    def sort(self):
        self.commands=collections.OrderedDict(sorted(self.commands.items()))