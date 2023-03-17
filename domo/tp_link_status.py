import sys
from PyP100 import PyP110 # pip install PyP100
try:
    P110_LOGIN = ""
    P110_PASS = ""
    p110 = PyP110.P110(sys.argv[1], P110_LOGIN, P110_PASS)
    p110.handshake()
    p110.login()
    stats = p110.getEnergyUsage()
    if(stats!=None and stats["result"]["current_power"]>0):
        print("1")
    else:
        print("0")
except:
    print("0")