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
 
def restartAsync():
    time.sleep(5)
    machine.reset()

class Program:
    def __init__(self):
        UTILS.init()
        self.cmdsWeb = self.createCmds("/?")
        self.cmdsBle = self.createCmds()
        self.ble = Ble(config.getValue(config._ble_name), self.cmdsBle)
        self.pin = PinOut(config.getValue(config._pinout_num))
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
        print(str(config.getValue(config._pin_button_toggle_on_off)))
        self.buttonOnOff = Button(config.getValue(config._pin_button_toggle_on_off), self.btn_pressed)
        
    def createCmds(self,prefix = ""):
        cmds = utils.Commands()
        cmds.add(prefix+"s_ssid", "set wifi ssid", self.setWifiSsid)
        cmds.add(prefix+"s_pass", "set wifi password", self.setWifiPassword)
        cmds.add(prefix+"s_ip", "set wifi ip", self.setWifiIp)
        cmds.add(prefix+"s_mask", "set wifi mask", self.setWifiMask)
        cmds.add(prefix+"s_gw", "set wifi gw", self.setWifiGw)
        cmds.add(prefix+"s_dns", "set wifi dns", self.setWifiDns)
        cmds.add(prefix+"s_pin_num", "set pin out number", self.setPinOut)
        cmds.add(prefix+"s_ble", "set bluetooth name", self.setPinBleName)
        cmds.add(prefix+"s_sep", "set command argument separator", self.setCmdSep)
        cmds.add(prefix+"s_endc", "set bluetooth command terminator character", self.setCmdEndChar)
        cmds.add(prefix+"restart", "restart", self.restart)
        cmds.add(prefix+"save", "save config", self.saveConfig)
        cmds.add(prefix+"s_meta", "use another config file", self.setConfFile)
        cmds.add(prefix+"g_status", "get pin status", self.getPinStatus)
        cmds.add(prefix+"s_off", "set output off", self.pinOff)
        cmds.add(prefix+"s_on", "set output on", self.pinOn)
        cmds.add(prefix+"g_config", "get current config", self.getCurrentConfig)
        cmds.add(prefix+"s_debug", "set debug flag", self.setDebug)
        cmds.add(prefix+"load_config", "reload config from current file", self.loadConfig)
        cmds.add(prefix+"help", "get all available commands", self.getAllCommands)
        cmds.sort()
        return cmds

    def getAllCommands(self):
        s = ""
        try:
            i = 2
            for key in self.cmdsBle.commands.keys():
                s += self.cmdsBle.commands[key].identifier + ' : ' + self.cmdsBle.commands[key].description
                if (i < len(self.cmdsBle.commands)):
                    s+="\n"
                i += 1
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
        _thread.start_new_thread(restartAsync,())
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
