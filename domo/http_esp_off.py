import sys
import http.client
try:
    http.client.HTTPConnection(sys.argv[1], 80).request("GET", "/?011-s_off")
    print("ok")
except:
    print("error")