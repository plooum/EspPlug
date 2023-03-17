import socket, sys
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((sys.argv[1],80))
    s.sendall("GET /?009-g_status HTTP/1.1\r\n\r\n".encode('utf-8'))
    print(s.recv(1024).decode('utf-8'))
except:
    print("/")