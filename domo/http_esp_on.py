import sys
import http.client
try:
    http.client.HTTPConnection(sys.argv[1], 80).request("GET", "/?010-s_on")
    print("ok")
except:
    print("error")