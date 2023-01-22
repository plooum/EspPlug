import config
from ble import Ble
from net import Network
from web import WebServer
from pinout import PinOut
from utils import UTILS
import utils
import time
import machine
import _thread
from button import Button
from security import Security
import os

def restartAsync():
    time.sleep(5)
    machine.reset()

class Program:
    def __init__(self):
        UTILS.init()
        self.cmdsWeb = self.createCmds()
        self.cmdsBle = self.createCmds()
        self.ble = Ble(config.getValue(config._ble_name), self.cmdsBle)
        self.pin = PinOut(int(config.getValue(config._pin_out)))
        self.network = Network(config.getValue(config._wifi_ssid),
                               utils.CIPHER.dec(config.getValue(config._wifi_password)),
                               config.getValue(config._wifi_ip),
                               config.getValue(config._wifi_mask),
                               config.getValue(config._wifi_gw),
                               config.getValue(config._wifi_dns),
                               self.startWebServer,
                               self.stopWebServer)
        self.webServer = WebServer(80, self.cmdsWeb, self.cmdsBle)
        self.startNetwork()
        self.buttonOnOff = Button(int(config.getValue(config._pin_in)), self.btn_pressed)
        s = Security()
    '''
    Ne pas mettre de ',' ni de ";" dans la description d'une commande.
    Ces caractères sont réservés pour la commande help :
        ',' : permet de séparer les champs "nom","description","nombre de paramètres".
        ';' : permet de séparer les commandes.
    '''
    def createCmds(self):
        cmds = utils.Commands()
        cmds.add("009-g_status", "get pin status", self.getPinStatus)
        cmds.add("010-s_on", "set output on", self.pinOn)
        cmds.add("011-s_off", "set output off", self.pinOff)
        cmds.add("050-s_ssid", "set wifi ssid", self.setWifiSsid, config._wifi_ssid, True)
        cmds.add("051-s_pass", "set wifi password", self.setWifiPassword, config._wifi_password, True)
        cmds.add("052-s_ip", "set wifi ip", self.setWifiIp, config._wifi_ip, True)
        cmds.add("053-s_mask", "set wifi mask", self.setWifiMask, config._wifi_mask, True)
        cmds.add("054-s_gw", "set wifi gw", self.setWifiGw, config._wifi_gw, True)
        cmds.add("055-s_dns", "set wifi dns", self.setWifiDns, config._wifi_dns, True)
        cmds.add("070-s_blename", "set bluetooth name", self.setBleName, config._ble_name, True)
        cmds.add("071-s_blepass", "set the bluetooth password", self.setBlePassword, "", True)
        cmds.add("080-s_pin_in0", "set pin in0 number", self.setPinIn, config._pin_in, True)
        cmds.add("120-s_pin_out0", "set pin out0 number", self.setPinOut, config._pin_out, True)
        cmds.add("180-s_sep", "set command argument separator", self.setCmdSep, config._cmd_separator, True)
        cmds.add("181-s_endc", "set command terminator character", self.setCmdEndChar, config._cmd_end_char, True)
        cmds.add("182-s_debug", "set debug flag", self.setDebug, config._debug, True)
        cmds.add("190-g_meta", "get meta conf avalaible", self.getMetaFiles)
        cmds.add("191-s_meta", "use another config file", self.setConfFile, "", True)
        cmds.add("200-g_config", "get current config", self.getCurrentConfig)
        cmds.add("210-load_config", "reload config from current file", self.loadConfig)
        cmds.add("220-save", "save config", self.saveConfig)
        cmds.add("250-restart", "restart", self.restart)
        cmds.add("help", "get all available commands", self.getAllCommands)
        cmds.sort()
        return cmds

    def getMetaFiles(self):
        metas = ""
        files = os.listdir()
        for file in files :
            if(".json" in file and "config" in file):
                file = file.replace(".json","")
                file = file.replace("config","")
                if (file.strip() != "" and file.strip() != "meta_"):
                    metas += file + chr(3)
        return metas
                

    def setBlePassword(self, newPassword):
        s = Security()
        if (not(s.change(newPassword))):
            raise Exception("")
        
    def getAllCommands(self):
        s = ""
        try:
            for key in self.cmdsBle.commands.keys():
                s += self.cmdsBle.commands[key].identifier + '|' + self.cmdsBle.commands[key].description + '|' + ("1" if self.cmdsBle.commands[key].takeParameters else "0" )
                s += chr(3)
        except Exception as e:
            utils.trace("Main : Error, " + str(e))
        return s
    
    def btn_pressed(self):
        if self.pin.getValue():
            self.pin.off()
        else:
            self.pin.on()
    
    def loadConfig(self):
        config.readFile()
    
    def setDebug(self, val):
        if (val == ""):
            raise Exception("")
        if val.lower()=="true" or val == "1":
            config.setValue(True, config._debug)
        else:
            config.setValue(False, config._debug)
    
    def getCurrentConfig(self):
        ret = ""
        for key in config.config_tab.keys():
            ret += key + '|"' + str(config.config_tab[key]) + '"'
            ret += chr(3)
        ret += "config file | " + config.file_config_name;
        ret += chr(3)
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
        _thread.start_new_thread(restartAsync,())
    
    def setWifiSsid(self, ssid):
        if (ssid == ""):
            raise Exception("")
        config.setValue(ssid, config._wifi_ssid)
    
    def setWifiPassword(self, password):
        if (password == ""):
            raise Exception("")
        config.setValue(utils.CIPHER.enc(password), config._wifi_password)
    
    def setWifiIp(self, ip):
        if (ip == ""):
            raise Exception("")
        config.setValue(ip, config._wifi_ip)
    
    def setWifiMask(self, mask):
        if (mask == ""):
            raise Exception("")
        config.setValue(mask, config._wifi_mask)
    
    def setWifiGw(self, gw):
        if (gw == ""):
            raise Exception("")
        config.setValue(gw, config._wifi_gw)
    
    def setWifiDns(self, dns):
        if (dns == ""):
            raise Exception("")
        config.setValue(dns, config._wifi_dns)
    
    def setPinOut(self, pinout_num):
        if (pinout_num == ""):
            raise Exception("")
        config.setValue(pinout_num, config._pin_out)
        
    def setPinIn(self, pinin_num):
        if (pinin_num == ""):
            raise Exception("")
        config.setValue(pinin_num, config._pin_in)
    
    def setBleName(self, ble_name):
        if (ble_name == ""):
            raise Exception("")
        config.setValue(ble_name, config._ble_name)
        
    def setCmdSep(self, cmd_separator):
        if (cmd_separator == ""):
            raise Exception("")
        config.setValue(cmd_separator, config._cmd_separator)
    
    def setCmdEndChar(self, cmd_ble_end_char):
        if (cmd_ble_end_char == ""):
            raise Exception("")
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
        
    def loopMain(self):
        while True:
            try:
                UTILS.freeMemory()
                self.webServer.update()
                self.network.update()
            except Exception:
                pass
    
    def stop(self):
        self.stopNetwork()
        self.stopWebServer()

if __name__ == "__main__":
    utils.trace("")
    utils.trace("Main : Starting program")
    utils.trace("")
    
    prog = Program()
    run = True

    try:
        while run:
            prog.loopMain()
    except KeyboardInterrupt:
        run = False
        pass
    except Exception as e:
        utils.trace("Main : Error, " + str(e))
        pass

    prog.stop()
    utils.trace("Main : Stopping program")
    utils.trace("")
