# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from urllib.parse import urlparse,parse_qs
from http.client import parse_headers
import json
import os
import socket
from subprocess import check_output
import html
import io
from ctypes import cdll 
import http.client
import json
import subprocess
from socketserver import ThreadingMixIn
import threading

hostName = ""
serverPort = 8282

_ROOT_FOLDER = "/home/domo/"

class MyServer(BaseHTTPRequestHandler):
    def getColorCssClass(self, colorName):
        colorCss = {}
        colorCss["blue"] = "btn-primary"
        colorCss["gray"] = "btn-secondary"
        colorCss["green"] = "btn-success"
        colorCss["red"] = "btn-danger"
        colorCss["yellow"] = "btn-warning"
        colorCss["turquoise"] = "btn-info"
        colorCss["white"] = "btn-light"
        colorCss["black"] = "btn-dark"
        colorCss["link"] = "btn-link"
        cssClass = ""
        try:
            cssClass = colorCss[colorName]
        except:
            pass
        return cssClass

    def process_action(self, var):
        var_device = None
        var_action = None
        var_special_action = None
        for key in var:
            if (key == "device"):
                var_device = var[key][0]
            if (key == "action"):
                var_action = var[key][0]
            if (key == "special_action"):
                var_special_action = var[key][0]
        if var_device != None and var_action != None:
            out = ""
            try:
                f = open(_ROOT_FOLDER + "config.json", "r")
                config = json.loads(f.read())
                command = config["plugs"][var_device]["actions"][var_action]["command"]
                arg = config["plugs"][var_device]["ip"]
                print('python3 ' + command + ' ' + arg)
                process = subprocess.Popen('python3 ' + command + ' ' + arg, stdout=subprocess.PIPE, shell=True)
                out, err = process.communicate()
            except:
                pass
            return out
        if var_device != None and var_special_action != None:
            out = ""
            try:
                f = open(_ROOT_FOLDER + "config.json", "r")
                config = json.loads(f.read())
                command = config["plugs"][var_device]["status"]["command"]
                if command != "":
                    arg = config["plugs"][var_device]["ip"]
                    process = subprocess.Popen('python3 ' + command + ' ' + arg, stdout=subprocess.PIPE, shell=True)
                    out, err = process.communicate()
                    return '{"result":"'+out.decode('utf-8').replace("\n","")+'"}'
            except Exception as e:
                print(e)
            return '{"result":"'+out+'"}'
        return None
    
    def get_html(self):
        f = open(_ROOT_FOLDER + "template_main.html", "r")
        template_data = f.read()
        f = open (_ROOT_FOLDER + "template_device.html", "r")
        template_device = f.read()
        f = open (_ROOT_FOLDER + "template_action.html", "r")
        template_action = f.read()
        f = open(_ROOT_FOLDER + "config.json", "r")
        config = json.loads(f.read())
        html_devices = ""
        for device in config["plugs"].keys():
            html_device = template_device.replace("%NAME%", device) + "\r\n"
            html_actions = ""
            for action in config["plugs"][device]["actions"].keys():
                html_action = template_action.replace("%ACTION%", action)
                html_action = html_action.replace("%DEVICE%", device)
                try:
                    css_class = self.getColorCssClass(config["plugs"][device]["actions"][action]["color"])
                except:
                    css_class = ""
                html_actions += html_action.replace("%CLASS%", css_class) + "\r\n"
            html_devices += html_device.replace("%ACTIONS%", html_actions)
        return template_data.replace("%DATA%", html_devices)
        
    def do_Request_Root(self, var):
        var_action = ""
        var_id = ""
        result = self.process_action(var)
        if result == None:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = self.get_html()
            self.wfile.write(bytes(html, "utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.end_headers()
            self.wfile.write(bytes(result, "utf-8"))
    
    def do_NotFound(self):
        form = """<html><head><title> ERROR 404 - Not Found</title></head>
<body>
Error 404, Requested URI not found
</body></html>"""
        self.send_response(404)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(form, "utf-8"))
        
    def do_Error(self, message):
        try:
            form = """<html><head><title> ERROR 501 - Error</title></head><body>
Error 501, """+message+"</body></html>"
            self.send_response(501)
            self.end_headers()
            self.wfile.write(bytes(form, "utf-8"))
        except:
            pass
    
    def do_HandleRequest(self, path, var):
        try:
            if(path == "/"):
                self.do_Request_Root(var)
            else:
                self.do_NotFound()
        except Exception as e:
            pass
            #self.do_Error(str(e))

    def do_GET(self):
        try:
            path = self.path
            action = ""
            game = ""
            var = {}
            if ("?" in path):
                var = {}
                var = parse_qs(path.split("?")[1])
                path = path.split("?")[0]
            # var -> la liste des variables 
            # path -> le chemin complet
            self.do_HandleRequest(path, var)
        except:
            pass
    
    def do_POST(self):
        try:
            svars = self.rfile.read(int(self.headers['content-length']))
            # print(svars)
            svars = svars.decode()
            var = parse_qs(svars)
            path = self.path
            self.do_HandleRequest(path, var)
        except:
            pass

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

if __name__ == '__main__':
    print("starting")
    webServer = None
    try:
        webServer = ThreadedHTTPServer((hostName, serverPort), MyServer)
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()

