import config
from net import Network
from web import WebServer
from pinout import PinOut
from utils import UTILS
import utils
import time
import machine
from button import Button
import gc
import webrepl

class Program:
    def __init__(self):
        utils.resetPending = False
        utils.lastConnected = time.time()
        self.first_run = True
        self.must_restart = -1
        UTILS.init()
        self.cmdsWeb = self.createCmds("")
        self.pin = PinOut(int(config.getValue(config._pinout_num)))
        self.network = Network(config.getValue(config._wifi_ssid),
                               utils.CIPHER.dec(config.getValue(config._wifi_password)),
                               config.getValue(config._wifi_ip),
                               config.getValue(config._wifi_mask),
                               config.getValue(config._wifi_gw),
                               config.getValue(config._wifi_dns),
                               self.startWebServer,
                               self.stopWebServer,
                               self.btn_pressed_long)
        self.webServer = WebServer(80, self.cmdsWeb)
        self.startNetwork()
        self.buttonOnOff = Button(int(config.getValue(config._pin_button)), self.btn_pressed_short, self.btn_pressed_long)
        self.led = PinOut(int(config.getValue(config._pin_led)))
        self.led.off()
        time.sleep(1)
        self.led.on() # inversé sur les sonoff basic R2 et les moes
        self.lastBlink = time.ticks_ms();
        self.blinkSpeed = 500
        self.start_blink_connected = time.time()
        self.blinkDuration = 0
        self.blink = False
        if (config.getValue(config._mode_wifi) == 1):
            self.startBlink(500)
        self.oldConnectionState = False
        self.run = True
        self.startDisconnected = False
        self.startDisconnecting = 0
        self.startTime = time.time()
        
    def createCmds(self,prefix = ""):
        cmds = utils.Commands()
        cmds.add(prefix+"000-s_name", "set name", self.setName,config._name, True)
        cmds.add(prefix+"001-g_name", "get name", self.getName, "", False, True)
        cmds.add(prefix+"009-g_status", "get status", self.getPinStatus)
        cmds.add(prefix+"010-s_on", "set on", self.pinOn)
        cmds.add(prefix+"011-s_off", "set off", self.pinOff)
        cmds.add(prefix+"040-s_pin_out0", "set pin out1 number (relay)", self.setPinOut0, config._pinout_num, True)
        cmds.add(prefix+"041-s_pin_in0", "set in0 pinnumber(button, sonoff : 0, moes :13)", self.setPinIn0, config._pin_button, True)
        cmds.add(prefix+"042-s_pin_outLed", "set out2 pinnumber (led, sonoff : 13, moes : 5)", self.setPinOutLed, config._pin_led, True)
        cmds.add(prefix+"050-s_ssid", "set wifi ssid", self.setWifiSsid, config._wifi_ssid, True)
        cmds.add(prefix+"051-s_pass", "set wifi password", self.setWifiPassword, config._wifi_password, True)
        cmds.add(prefix+"052-s_ip", "set wifi ip", self.setWifiIp, config._wifi_ip, True)
        cmds.add(prefix+"053-s_mask", "set wifi mask", self.setWifiMask, config._wifi_mask, True)
        cmds.add(prefix+"054-s_gw", "set wifi gw", self.setWifiGw, config._wifi_gw, True)
        cmds.add(prefix+"055-s_dns", "set wifi dns", self.setWifiDns, config._wifi_dns, True)
        cmds.add(prefix+"182-s_debug", "set debug flag", self.setDebug, config._debug, True)
        cmds.add(prefix+"185-s_meta", "use another config file", self.setConfFile, "", True)
        cmds.add(prefix+"190-g_mem", "get mem used and free", self.getMem)
        cmds.add(prefix+"200-g_config", "get current config", self.getCurrentConfig, "", False, True)
        cmds.add(prefix+"210-load_config", "reload config from current file", self.loadConfig)
        cmds.add(prefix+"220-save", "save config", self.saveConfig)
        cmds.add(prefix+"250-restart", "restart", self.restart)
        cmds.add(prefix+"260-wifimode", "change the wifi mode", self.changeModeWifi)
        cmds.add(prefix+"help", "help", self.getAllCommands, "", False, True)
        cmds.sort()
        return cmds
    
    def startBlink(self, speed, duration = -1):
        self.blink = True
        self.blinkSpeed = speed
        self.blinkDuration = duration
    
    def surveyStopBlink(self):
        if(self.blinkDuration > 0):
            cur = time.time()
            if (cur < self.start_blink_connected):
                self.start_blink_connected = cur
            if(cur - self.start_blink_connected > self.blinkDuration):
                self.blink = False
                self.led.on()
    
    def updateBlink(self):
        if(self.blink):
            cur_ms = time.ticks_ms()
            if(cur_ms < self.lastBlink):
                self.lastBlink = 0;
            if(cur_ms - self.lastBlink > self.blinkSpeed):
                self.lastBlink = cur_ms
                if self.led.getValue():
                    self.led.off()
                else:
                    self.led.on()
                    
    def getMem(self):
        return "{} / {}".format(gc.mem_alloc(), gc.mem_alloc() + gc.mem_free())
                    
    def setName(self, ble_name):
        config.setValue(ble_name, config._name)
     
    def getName(self, sendCallback):
        sendCallback(config.getValue(config._name))
    
    def getAllCommands(self, sendCallback):
        try:
            for key in self.cmdsWeb.commands.keys():
                sendCallback(self.cmdsWeb.commands[key].identifier + '|' + self.cmdsWeb.commands[key].description + '|' + ("1" if self.cmdsWeb.commands[key].takeParameters else "0" ) + chr(3))
        except Exception:
            pass
#             utils.trace("Main : Error, " + str(e))
    
    def btn_pressed_short(self):
        if self.pin.getValue():
            self.pin.off()
        else:
            self.pin.on()
    
    def changeModeWifi(self):
        val = config.getValue(config._mode_wifi)
        if(val == 0):
            val = 1
        else:
            val = 0
        config.setValue(val, config._mode_wifi)
        self.saveConfig()
        self.restart()
        print("")
    
    def btn_pressed_long(self):
        for i in range(0, 10):
            self.led.off()
            time.sleep(0.05)
            self.led.on()
            time.sleep(0.05)
        self.changeModeWifi()
    
    def loadConfig(self):
        config.readFile()
        
    def setDebug(self, val):
        if val.lower()=="true" or val == "1":
            config.setValue(True, config._debug)
        else:
            config.setValue(False, config._debug)
    def getCurrentConfig(self, sendCallback):
        for key in config.config_tab.keys():
            sendCallback(key + '|"' + str(config.config_tab[key]) + '"' + chr(3))
        sendCallback('config file|"' + config.file_config_name + '"')
    
    def getPinStatus(self):
        if self.pin.getValue():
            return "1"
        else:
            return "0"
        
    def setConfFile(self,name):
        config.setMetaConf(name)

    def saveConfig(self):
        config.writeFile()
        
    def restart(self):
        self.must_restart = time.time()
        self.blink = False
        self.led.off()
        
    def setWifiSsid(self, ssid):
        config.setValue(ssid, config._wifi_ssid)
        
    def setWifiPassword(self, password):
        config.setValue(utils.CIPHER.enc(password), config._wifi_password)
        
    def setWifiIp(self, ip):
        config.setValue(ip, config._wifi_ip)
    
    def setWifiGw(self, gw):
        config.setValue(gw, config._wifi_gw)
    
    def setWifiDns(self, dns):
        config.setValue(dns, config._wifi_dns)
    
    def setWifiMask(self, mask):
        config.setValue(mask, config._wifi_mask)
        
    def setPinIn0(self, pinin_num):
        config.setValue(pinin_num, config._pin_button)

    def setPinOut0(self, pinout_num):
        config.setValue(pinout_num, config._pinout_num)

    def setPinOutLed(self, pinout_num):
        config.setValue(pinout_num, config._pin_led)
        
    def setPinBleName(self, ble_name):
        config.setValue(ble_name, config._name)
        
    def setCmdSep(self, cmd_separator):
        config.setValue(cmd_separator, config._cmd_separator)
        
    def setCmdEndChar(self, cmd_ble_end_char):
        config.setValue(cmd_ble_end_char, config._cmd_ble_end_char)
        
    def pinOn(self):
        self.pin.on()
        
    def pinOff(self):
        self.pin.off()

    def startNetwork(self):
        utils.trace("Main : Starting Network")
        self.network.start()
        
    def stopNetwork(self):
        utils.trace("Main : Stopping Network")
        self.network.stop()
    
    def startWebServer(self):
        utils.trace("Main : Starting WebServer")
        self.webServer.start()
        
    def stopWebServer(self):
        utils.trace("Main : Stopping WebServer")
        self.webServer.stop()
    
    def updateRestart(self):
        if (self.must_restart > -1):
            if(time.time() - self.must_restart > 4):
                machine.reset()
                self.run = False
    
    def updateSurveyConnectionState(self):
        cur = time.time()
        if (config.getValue(config._mode_wifi) == 0):
            state = self.network.isConnected()
            disconnected = False
            if (not(self.oldConnectionState) and state):
                self.startBlink(250,5)
                self.oldConnectionState = True
                self.startDisconnected = False
            elif(self.oldConnectionState and not(state)):
                self.oldConnectionState = False
                disconnected = True
            elif(self.first_run and not(state)):
                disconnected = True

            if (disconnected):
                if(not(self.startDisconnected)):
                    self.startBlink(30)
                    self.startDisconnecting = cur
                    self.startDisconnected = True

            if(self.startDisconnected):
                if(self.startDisconnecting > cur):
                    self.startDisconnecting = cur
                dif = cur - self.startDisconnecting
                if(dif > 30):
                    self.changeModeWifi()
                    utils.resetPending = True
            
        elif(not(utils.resetPending)):
            if(utils.lastConnected > cur):
                utils.lastConnected = cur
            dif = cur - utils.lastConnected
            if(dif > 300):
                self.changeModeWifi()
    
    def loopMain(self):
        self.network.startOnce()
        self.run = True
        while self.run:
            try:
                UTILS.freeMemory()
                self.webServer.update()
                self.updateRestart()
                self.updateBlink()
                self.surveyStopBlink()
                self.buttonOnOff.update()
                self.updateSurveyConnectionState()
                self.first_run = False
                time.sleep(0.05)
            except KeyboardInterrupt:
                self.run = False
                pass
            except Exception:
                pass
    
    def stop(self):
        self.stopNetwork()
        self.stopWebServer()
        self.led.on() # inversé sur sonoff et moes

def main():
    utils.trace("Main : Starting program")
    prog = Program()
    prog.loopMain()
    prog.stop()
    utils.trace("Main : Stopping program")

main()
