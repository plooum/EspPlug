import config
from net import Network
from web import WebServer
from pinout import PinOut
from utils import UTILS
import utils
import time
import machine
from button import Button
from security import Security
import sys

class Program:
    def __init__(self):
        self.must_restart = -1
        UTILS.init()
        self.cmdsWeb = self.createCmds("/?")
        self.pin = PinOut(12)
        self.network = Network(config.getValue(config._wifi_ssid),
                               utils.CIPHER.dec(config.getValue(config._wifi_password)),
                               config.getValue(config._wifi_ip),
                               config.getValue(config._wifi_mask),
                               config.getValue(config._wifi_gw),
                               config.getValue(config._wifi_dns),
                               self.startWebServer,
                               self.stopWebServer)
        self.cmdsBle = {}
        self.webServer = WebServer(80, self.cmdsWeb, self.cmdsBle)
        self.startNetwork()
        self.buttonOnOff = Button(config.getValue(config._pin_button_toggle_on_off), self.btn_pressed_short, self.btn_pressed_long)
        self.led = PinOut(13)
        self.led.on() # c'est inversé sur les sonoff basic R2
        self.lastBlink = time.ticks_ms();
        if (config.getValue(config._mode_wifi) == 1):
            self.blink = True
        else:
            self.blink = False

    '''
    Ne pas mettre de ',' ni de ";" dans la description d'une commande.
    Ces caractères sont réservés pour la commande help :
        ',' : permet de séparer les champs "nom","description","nombre de paramètres".
        ';' : permet de séparer les commandes.
    '''
    def createCmds(self,prefix = ""):
        cmds = utils.Commands()
        cmds.add(prefix+"s_ssid", "set wifi ssid", self.setWifiSsid, True)
        cmds.add(prefix+"s_pass", "set wifi password", self.setWifiPassword, True)
#         cmds.add(prefix+"s_ip", "set wifi ip", self.setWifiIp, True)
#         cmds.add(prefix+"s_mask", "set wifi mask", self.setWifiMask, True)
#         cmds.add(prefix+"s_gw", "set wifi gw", self.setWifiGw, True)
#         cmds.add(prefix+"s_dns", "set wifi dns", self.setWifiDns, True)
#         cmds.add(prefix+"s_pin_num", "set pin out number", self.setPinOut, True)
#         cmds.add(prefix+"s_blename", "set bluetooth name", self.setPinBleName, True)
#         cmds.add(prefix+"s_sep", "set command argument separator", self.setCmdSep, True)
#         cmds.add(prefix+"s_endc", "set bluetooth command terminator character", self.setCmdEndChar, True)
        cmds.add(prefix+"restart", "restart", self.restart)
        cmds.add(prefix+"save", "save config", self.saveConfig)
        cmds.add(prefix+"s_meta", "use another config file", self.setConfFile, True)
        cmds.add(prefix+"g_status", "get pin status", self.getPinStatus)
        cmds.add(prefix+"s_off", "set output off", self.pinOff)
        cmds.add(prefix+"s_on", "set output on", self.pinOn)
        cmds.add(prefix+"g_config", "get current config", self.getCurrentConfig)
        cmds.add(prefix+"s_debug", "set debug flag", self.setDebug, True)
        cmds.add(prefix+"load_config", "reload config from current file", self.loadConfig)
        cmds.add(prefix+"help", "get all available commands", self.getAllCommands)
#         cmds.add(prefix+"s_blepass", "set the bluetooth password", self.setBlePassword, True)
        cmds.add(prefix+"wifimode", "toggle change the wifi mode", self.changeModeWifi)
        cmds.sort()
        return cmds
    
    def updateBlink(self):
        if(self.blink):
            cur_ms = time.ticks_ms()
            if(cur_ms < self.lastBlink):
                self.lastBlink = 0;
            if(cur_ms - self.lastBlink > 500):
                self.lastBlink = cur_ms
                if self.led.getValue():
                    self.led.off()
                else:
                    self.led.on()
    
    def setBlePassword(self, newPassword):
        s = Security()
        if (not(s.change(newPassword))):
            raise Exception("")
        
    def getAllCommands(self):
        s = ""
        try:
            for key in self.cmdsWeb.commands.keys():
                s += self.cmdsWeb.commands[key].identifier + ',' + self.cmdsWeb.commands[key].description + ',' + ("1" if self.cmdsWeb.commands[key].takeParameters else "0" ) + ";"
        except Exception as e:
            utils.trace("Main : Error, " + str(e))
        return s
    
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
        self.blink = False
        self.led.off()
        self.restart()
    
    def btn_pressed_long(self):
        self.changeModeWifi()
    
    def loadConfig(self):
        config.readFile()
        
    def setDebug(self, val):
        if val.lower()=="true" or val == "1":
            config.setValue(True, config._debug)
        else:
            config.setValue(False, config._debug)
    def getCurrentConfig(self):
        ret = ""
        for key in config.config_tab.keys():
            ret += key + ' : "' + str(config.config_tab[key]) + '"\r\n'
        ret += "config file : " + config.file_config_name;
        return ret
    
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
        
    def setWifiSsid(self, ssid):
        config.setValue(ssid, config._wifi_ssid)
        
    def setWifiPassword(self, password):
        config.setValue(utils.CIPHER.enc(password), config._wifi_password)
        
    def setWifiIp(self, ip):
        config.setValue(ip, config._wifi_ip)
        
    def setWifiMask(self, mask):
        config.setValue(mask, config._wifi_mask)
        
    def setWifiGw(self, gw):
        config.setValue(gw, config._wifi_gw)
        
    def setWifiDns(self, dns):
        config.setValue(dns, config._wifi_dns)
        
    def setPinOut(self, pinout_num):
        config.setValue(pinout_num, config._pinout_num)
        
    def setPinBleName(self, ble_name):
        config.setValue(ble_name, config._ble_name)
        
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
            if(time.time() - self.must_restart > 3):
                machine.reset()
    
    def loopMain(self):
        run = True
        while run:
            try:
                UTILS.freeMemory()
                self.webServer.update()
                self.network.update()
                self.updateRestart()
                self.updateBlink()
            except KeyboardInterrupt:
                run = False
                pass
            except Exception as e:
                utils.trace("Main, Error : " + str(e))
                pass
    
    def stop(self):
        self.stopNetwork()
        self.stopWebServer()
        self.led.on()

def main():
    utils.trace("")
    utils.trace("Main : Starting program")
    utils.trace("")
    
    prog = Program()
    prog.loopMain()
    
    prog.stop()
    utils.trace("Main : Stopping program")
    utils.trace("")

main()
