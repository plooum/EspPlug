from time import time,sleep
import network
import utils
import config

stopUpdate = False

class Network:
    def __init__(self,ssid, password, ip, mask, gw, dns, callbackConnected, callbackDisconnected):
        self.falgIsConnected = False
        self._ssid = ssid
        self._password = password
        self._ip = ip
        self._mask = mask
        if (self._mask is None or self._mask == ""):
            self._mask = "255.255.255.0"
        self._gw = gw
        if (self._gw is None or self._gw == ""):
            ips = self._ip.split(".")
            if len(ips) > 2:
                self._gw = ips[0] + '.' + ips[1] + '.' +ips[2] + '.1' 
        self._dns = dns
        if (self._dns is None or self._dns == ""):
            ips = self._ip.split(".")
            if len(ips) > 2:
                self._dns = ips[0] + '.' + ips[1] + '.' +ips[2] + '.1' 
        self.callbackConnected = callbackConnected
        self.callbackDisconnected = callbackDisconnected
        if (config.getValue(config._mode_wifi) == 1):
            utils.trace("WIFI : init AP -> SSID = sonoff, Pass = 123456789")
            self.wlan = network.WLAN(network.AP_IF)
            self.wlan.active(True)                
            self.wlan.config(essid="sonoff", password="123456789")
            while not(self.wlan.active()):
                pass
        else:
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.active(True)
            if (self._ip is not None and self._ip != ""):
                self.wlan.ifconfig((self._ip, self._mask, self._gw, self._dns)) # IP fixe sinon supprimer la ligne
        self.lastConnectionAttempt = -10000
        self.nbSecondsBetweenAttempts = 600
        self.stop_ = False
        
    def connect(self):
        if (config.getValue(config._mode_wifi) == 0):
            if(self.lastConnectionAttempt > time()):
                self.lastConnectionAttempt = -10000
            if((time() - self.lastConnectionAttempt) > self.nbSecondsBetweenAttempts):
                self.lastConnectionAttempt = time()
                utils.trace("WIFI : Connecting")
                self.wlan.connect(self._ssid, self._password)
        else:
            self.falgIsConnected = True
    
    def isConnected(self):
        if (config.getValue(config._mode_wifi) == 0):
            isConnected = False
            try:
                isConnected = self.wlan.isconnected()
            except Exception as e:
                utils.trace("WIFI : Error, " + str(e))
                pass
            return isConnected
        else:
            return self.falgIsConnected
    
    def start(self):
        self.stop_ = False
        
    def stop(self):
        self.stop_ = True
        self.wlan.active(False)
        self.falgIsConnected = False
        
    def isRunning(self):
        return not (self.stop_)
    
    def startOnce(self):
        self.connect()
        if (config.getValue(config._mode_wifi) == 0):
            maxWait = 15
            lastTime = time()
            while(not(self.isConnected()) and time()-lastTime < maxWait):
                sleep(0.1)
            utils.trace(str(self.wlan.ifconfig()))
        if(self.callbackConnected() is not None):
            self.callbackConnected()

    def update(self):
        global stopUpdate
        try:
            if(not (stopUpdate)):
                if(self.isRunning()):
                    if(not (self.isConnected())):
                        try:
                            self.connect()
                        except Exception as e: 
                            utils.trace("WIFI : Connect Error : "+str(e))
                        if (config.getValue(config._mode_wifi) == 0):
                            maxWait = 5
                            lastTime = time()
                            while(not(self.isConnected()) and time()-lastTime < maxWait):
                                sleep(0.1)
                        if(self.isConnected()):
                            utils.trace("WIFI : Connected")
                            utils.trace(str(self.wlan.ifconfig()))
                            if(self.callbackConnected() is not None):
                                self.callbackConnected()
                                stopUpdate = True
                        else:
                            utils.trace("WIFI : Unable to connect")
                            if(self.callbackDisconnected() is not None):
                                self.callbackDisconnected()
        except Exception as e: 
            utils.trace("WIFI : Error, "+str(e))