import socket
import utils
import time
import config

class WebServer:
    def __init__(self, port, commands):
        self.commands = commands
        self.port = port
        self.started = False
        self.bleCmds = commands
        self.curCli = None
        
    def start(self):
        utils.trace("WebServer : Started")
        self.started = True
        self.socketServeur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketServeur.bind(('', self.port))
        self.socketServeur.listen(5)
        self.socketServeur.settimeout(0.01)
        
    def stop(self):
        self.started = False
    
    def isStarted(self):
        return self.started
    
    def update(self):
        if(self.isStarted()):
            try:
                connectionCli = None
                try:
                    connectionCli, address = self.socketServeur.accept()
                except KeyboardInterrupt:
                    raise KeyboardInterrupt
                except:
                    pass
                if (connectionCli is not None):
                    self.curCli = connectionCli
                    utils.trace("WebServer : Request from : " + str(address))
                    utils.lastConnected = time.time()
                    connectionCli.settimeout(1)
                    request = None
                    try:
                        request = connectionCli.recv(512)
                    except:
                        pass
                    if request is not None:
                        request = str(request.decode('utf-8'))
                        hasCmd = False
                        hasReturnValue = False
                        hasError = False
                        returnValue = None
                        for key_ in self.commands.commands.keys():
                            key = "/?" + key_
                            if key in request:
                                lines = request.split("\n")
                                for line in lines:
                                    if key in line:
                                        words = line.split()
                                        for word in words:
                                            if key in word:
                                                hasCmd = True
                                                if (self.commands.commands[key_].takeCallback):
                                                    self.commands.commands[key_].executeCallback(self.send)
                                                    hasReturnValue = True
                                                else:
                                                    args = word.split(config.getValue(config._cmd_separator))
                                                    if len(args) > 1:
                                                        argv = args[1]
                                                        cnt = len(args)
                                                        for i in range(2, cnt):
                                                            argv += config.getValue(config._cmd_separator) + args[i]
                                                        returnValue = self.commands.commands[key_].execute(argv)
                                                    else:
                                                        if self.commands.commands[key_].takeParameters:
                                                            try:
                                                                returnValue = self.commands.commands[key_].execute("")
                                                            except:
                                                                utils.trace("WebServer : Error, "+str(e))
                                                                hasError = True
                                                                returnValue = None
                                                        else:
                                                            try:
                                                                returnValue = self.commands.commands[key_].execute()
                                                            except:
                                                                utils.trace("WebServer : Error, "+str(e))
                                                                hasError = True
                                                                returnValue = None
                                                    if returnValue is not None:
                                                        hasReturnValue = True
                                                        connectionCli.sendall(str(returnValue))
                                if (not hasReturnValue):
                                    if hasError:
                                        connectionCli.sendall("ERROR")
                                    else:
                                        connectionCli.sendall("OK")
                        if (not(hasCmd)):
                            self.sendHtml(connectionCli) 
                        connectionCli.close()
                    self.curCli = None
            except Exception:
                pass
                
    def send(self, msg):
        self.curCli.sendall(str(msg))
        
    def sendHtml(self, connectionCli): 
        with open("template.html", 'r') as file :
            for line in file:
                line = line.replace("\n", "")
                line = line.replace("\r", "")
                if(line == "%title%"):
                    connectionCli.sendall(config.getValue(config._name))
                elif(line == "%commands%"):
                    i=0
                    for key in self.commands.commands.keys():
                        connectionCli.sendall("<tr>")
                        connectionCli.sendall("\t<td><b>" + self.commands.commands[key].description + "</b>\r\n")
                        connectionCli.sendall("<br>" + self.commands.commands[key].identifier + "\r\n")
                        connectionCli.sendall("\t<br><button class=\"btn btn-secondary\" style=\"background-color: lightgray !important;color: black;\" onclick=\"ajax('"+self.commands.commands[key].identifier + "', '"+str(i)+"')\">" + "Send"+"</button>"+"</td>\r\n")
                        if (self.commands.commands[key].takeParameters):
                            connectionCli.sendall('\t<td><input class="form-control" id="input'+str(i)+'" value="'+ str(config.getValue(self.commands.commands[key].configKey))+'" type="text">\r\n')
                            connectionCli.sendall('\t<br><div id="res'+str(i)+'"></div></td>\r\n')
                        else:
                            connectionCli.sendall('\t<td><div id="res'+str(i)+'"></div></td>\r\n')
                        connectionCli.sendall("</tr>")
                        i+=1
                else:
                    connectionCli.sendall(line+"\r\n")