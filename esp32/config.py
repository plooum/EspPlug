import utils
import json
import collections

config_keys = []

file_config_name = "config.json"
_meta_conf_key = "name"

config_tab = {}

_wifi_ssid = "wifi_ssid"
_wifi_password = "wifi_password"
_wifi_ip = "wifi_ip"
_wifi_mask = "wifi_mask"
_wifi_gw = "wifi_gw"
_wifi_dns = "wifi_dns"
_ble_name = "ble_name"
_cmd_separator = "cmd_separator"
_cmd_end_char = "cmd_end_char"
_debug = "debug"
_pin_in = "pin_in0"
_pin_out = "pin_out0"

config_keys.append(_wifi_ssid)
config_keys.append(_wifi_password)
config_keys.append(_wifi_ip)
config_keys.append(_wifi_mask)
config_keys.append(_wifi_gw)
config_keys.append(_wifi_dns)
config_keys.append(_pin_out)
config_keys.append(_ble_name)
config_keys.append(_cmd_separator)
config_keys.append(_cmd_end_char)
config_keys.append(_debug)
config_keys.append(_pin_in)
config_keys.sort()

def loadDefaultValues():
    global config_tab
    if(not(_pin_out in config_tab.keys()) or str(config_tab[_pin_out]) == ""):
        config_tab[_pin_out] = 12
    if(not(_ble_name in config_tab.keys()) or str(config_tab[_ble_name]) == ""):
        config_tab[_ble_name] = "ESP32"
    if(not(_cmd_separator in config_tab.keys()) or str(config_tab[_cmd_separator]) == ""):
        config_tab[_cmd_separator] = "="
    if(not(_cmd_end_char in config_tab.keys()) or str(config_tab[_cmd_end_char]) == ""):
        config_tab[_cmd_end_char] = ";"
    if(not(_debug in config_tab.keys()) or str(config_tab[_debug]) == ""):
        config_tab[_debug] = True
    if(not(_pin_in in config_tab.keys()) or str(config_tab[_pin_in]) == ""):
        config_tab[_pin_in] = 0
    for key in config_keys:
        if(not(key in config_tab.keys())):
            config_tab[key] = ""
    sort()
    
def readMetaConf():
    global file_config_name
    try:
        meta_config_tab = {}
        f = open("meta_config.json", 'r')
        meta_config_tab = json.loads(f.read())
        file_config_name = "config" + str(meta_config_tab[_meta_conf_key]) + ".json"
    except Exception as e:
        meta_config_tab = {}
        file_config_name = "config.json"
        meta_config_tab[_meta_conf_key] = file_config_name
        raise

def setMetaConf(numConf):
    meta_config_tab = {}
    meta_config_tab[_meta_conf_key] = str(numConf)
    f = open("meta_config.json", 'w')
    f.write(json.dumps(meta_config_tab))
    f.close()
    try:
        readMetaConf()
    except:
        pass

def readFile():
    global config_tab
    utils.trace("Config : Reading file, " + str(file_config_name))
    try:
        f = open(file_config_name, 'r')
        s = f.read()
        config_tab = json.loads(s)
        loadDefaultValues()
    except Exception as e:
        utils.trace("Config : Error, " + str(e))
        config_tab = {}
        raise

def writeFile():
    global config_tab
    utils.trace("Config : Writing file, " + str(file_config_name))
    try:
        f = open(file_config_name, 'w')
        f.write(json.dumps(config_tab))
        f.close()
    except Exception as e:
        utils.trace("Config : Error, " + str(e))
        raise

def sort():
    global config_tab
    try:
        config_tab=collections.OrderedDict(sorted(config_tab.items()))
    except:
        pass

def getValue(key):
    global config_tab
    if (key == ""):
        return ""
    try:
        if key in config_tab.keys():
            return config_tab[key]
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
    setMetaConf("")
    pass

try:
    readFile()
    loadDefaultValues()
except:
    loadDefaultValues()
    writeFile()
    pass

