from time import time,sleep
import network
import _thread
import utils

class Network:
    def __init__(self,ssid, password, ip, mask, gw, dns, callbackConnected, callbackDisconnected):
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
        self.wlan = network.WLAN(network.STA_IF)
        self.lastConnectionAttempt = -10000
        self.nbSecondsBetweenAttempts = 600
        self.callbackConnected = callbackConnected
        self.callbackDisconnected = callbackDisconnected
        self.stop_ = False
        
    def connect(self):
        if(self.lastConnectionAttempt > time()):
            self.lastConnectionAttempt = -10000
        if((time() - self.lastConnectionAttempt) > self.nbSecondsBetweenAttempts):
            self.lastConnectionAttempt = time()
            utils.trace("WIFI : Connecting")
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.ifconfig((self._ip, self._mask, self._gw, self._dns)) # IP fixe sinon supprimer la ligne
            self.wlan.active(True)
            self.wlan.connect(self._ssid, self._password)
    
    def isConnected(self):
        isConnected = False
        try:
            isConnected = self.wlan.isconnected()
        except:
            pass
        return isConnected
    
    def start(self):
        self.stop_ = False
        
    def stop(self):
        self.stop_ = True
        self.wlan.active(False)
        
    def isRunning(self):
        return not (self.stop_)
    
    def update(self):
        try:
            if(self.isRunning()):
                if(not (self.wlan.isconnected())):
                    self.connect()
                    maxWait = 4
                    lastTime = time()
                    while(not(self.isConnected()) and time()-lastTime < maxWait):
                        sleep(0.1)
                    if(self.isConnected()):
                        utils.trace("WIFI : Connected")
                        if(self.callbackConnected() is not None):
                            self.callbackConnected()
                    else:
                        utils.trace("WIFI : Unable to connect")
                        if(self.callbackDisconnected() is not None):
                            self.callbackDisconnected()
        except Exception as e: 
            utils.trace("WIFI Error : "+str(e))