import utils
import json
import collections

config_keys = []

file_config_name = "config.json"
_meta_conf_key = "meta"

config_tab = {}

_wifi_ssid = "wifi_ssid"
_wifi_password = "wifi_password"
_wifi_ip = "wifi_ip"
_wifi_mask = "wifi_mask"
_wifi_gw = "wifi_gw"
_wifi_dns = "wifi_dns"
_pinout_num = "pinout_num"
_name = "name"
_cmd_separator = "cmd_separator"
_debug = "debug"
_pin_button = "pin_button"
_pin_led = "pin_led"
_mode_wifi = "mode_wifi"

config_keys.append(_wifi_ssid)
config_keys.append(_wifi_password)
config_keys.append(_wifi_ip)
config_keys.append(_wifi_mask)
config_keys.append(_wifi_gw)
config_keys.append(_wifi_dns)
config_keys.append(_pinout_num)
config_keys.append(_name)
config_keys.append(_cmd_separator)
config_keys.append(_debug)
config_keys.append(_pin_button)
config_keys.append(_mode_wifi)
config_keys.append(_pin_led)
config_keys.sort()

def loadDefaultValues():
    global config_tab
    if(not(_pinout_num in config_tab.keys()) or str(config_tab[_pinout_num]) == ""):
        config_tab[_pinout_num] = 12
    if(not(_name in config_tab.keys()) or str(config_tab[_name]) == ""):
        config_tab[_name] = "PL"
    if(not(_cmd_separator in config_tab.keys()) or str(config_tab[_cmd_separator]) == ""):
        config_tab[_cmd_separator] = "="
    if(not(_debug in config_tab.keys()) or str(config_tab[_debug]) == ""):
        config_tab[_debug] = True
    if(not(_pin_button in config_tab.keys()) or str(config_tab[_pin_button]) == ""):
        config_tab[_pin_button] = 0 #13
    if(not(_mode_wifi in config_tab.keys()) or str(config_tab[_mode_wifi]) == ""):
        config_tab[_mode_wifi] = 1
    if(not(_pin_led in config_tab.keys()) or str(config_tab[_pin_led]) == ""):
        config_tab[_pin_led] = 13 #5
    for key in config_keys:
        if(not(key in config_tab.keys())):
            config_tab[key] = ""
    sort()
    
def getMetaConf():
    try:
        meta_config_tab = {}
        f = open("meta_config.json", 'r')
        meta_config_tab = json.loads(f.read())
        return meta_config_tab[_meta_conf_key]
    except:
        return ""

def readMetaConf():
    global file_config_name
    try:
        meta_config_tab = {}
        f = open("meta_config.json", 'r')
        meta_config_tab = json.loads(f.read())
        file_config_name = "config" + str(meta_config_tab[_meta_conf_key]) + ".json"
    except Exception as e:
        print (str(e))

def setMetaConf(numConf):
    meta_config_tab = {}
    meta_config_tab[_meta_conf_key] = str(numConf)
    f = open("meta_config.json", 'w')
    f.write(json.dumps(meta_config_tab))
    f.close()
    readMetaConf()

def readFile():
    global config_tab
    utils.trace("Config : Reading file, " + str(file_config_name))
    try:
        f = open(file_config_name, 'r')
        s = f.read()
        config_tab = json.loads(s)
        loadDefaultValues()
    except Exception:
        config_tab = {}
        raise

def writeFile():
    global config_tab
    utils.trace("Config : Writing file, " + str(file_config_name))
    try:
        f = open(file_config_name, 'w')
        f.write(json.dumps(config_tab))
        f.close()
    except Exception:
        raise

def sort():
    global config_tab
    try:
        config_tab=collections.OrderedDict(sorted(config_tab.items()))
    except:
        pass

def getValue(key):
    global config_tab
    try:
        if key in config_tab.keys():
            return config_tab[key]
        elif key == _meta_conf_key:
            return getMetaConf()
    except:
        pass
    return ""

def setValue(value, key):
    global config_tab
    utils.trace("Config : Setting "+key+" = "+str(value))
    try:
        config_tab[key] = value
    except:
        pass

try:
    readMetaConf()
except:
    pass
try:
    readFile()
except:
    pass
loadDefaultValues()