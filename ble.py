import bluetooth
from micropython import const
import utils
import config
import time
from security import Security

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
#_IRQ_GATTS_READ_REQUEST = const(4)
#_IRQ_SCAN_RESULT = const(5)
#_IRQ_SCAN_DONE = const(6)
#_IRQ_PERIPHERAL_CONNECT = const(7)
#_IRQ_PERIPHERAL_DISCONNECT = const(8)
#_IRQ_GATTC_SERVICE_RESULT = const(9)
#_IRQ_GATTC_SERVICE_DONE = const(10)
#_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
#_IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
#_IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
#_IRQ_GATTC_DESCRIPTOR_DONE = const(14)
#_IRQ_GATTC_READ_RESULT = const(15)
#_IRQ_GATTC_READ_DONE = const(16)
#_IRQ_GATTC_WRITE_DONE = const(17)
#_IRQ_GATTC_NOTIFY = const(18)
#_IRQ_GATTC_INDICATE = const(19)
#_IRQ_GATTS_INDICATE_DONE = const(20)
#_IRQ_MTU_EXCHANGED = const(21)
#_IRQ_L2CAP_ACCEPT = const(22)
#_IRQ_L2CAP_CONNECT = const(23)
#_IRQ_L2CAP_DISCONNECT = const(24)
#_IRQ_L2CAP_RECV = const(25)
#_IRQ_L2CAP_SEND_READY = const(26)
#_IRQ_CONNECTION_UPDATE = const(27)
#_IRQ_ENCRYPTION_UPDATE = const(28)
#_IRQ_GET_SECRET = const(29)
#_IRQ_SET_SECRET = const(30)

WAITING_PASSWORD = 0
PASSWORD_VERIFIED = 1
BLOCKED = 2

end_password_char = ';'

class Ble():
    def __init__(self, name, commands):
        self.name = name
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self.ble_irq)
        self.register()
        self.startAdvertise()
        self.commands = commands
        self.msg = ""
        self.state = WAITING_PASSWORD
        self.input_password = ""
        
    def connected(self):
        utils.trace("BLE : Connected")
        self.stopAdvertise()
    
    def disconnected(self):
        utils.trace("BLE : Disconnected")
        self.startAdvertise()

    def ble_irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            self.connected()
            self.conn_handle, addr_type, addr = data
            self.state = WAITING_PASSWORD
            self.input_password = ""
            
        elif event == _IRQ_CENTRAL_DISCONNECT:
            self.disconnected()
            self.conn_handle = None
        
        elif event == _IRQ_GATTS_WRITE:
            buffer = self.ble.gatts_read(self.rx)
            message = buffer.decode('UTF-8').strip()
            utils.trace("BLE : Message received, " + message)
            if (self.state == WAITING_PASSWORD):
                self.input_password += message
                if(len(self.input_password)>51):
                    self.state = BLOCKED
                if (end_password_char in self.input_password):
                    buf= self.input_password.split(end_password_char)[0]
                    security = Security()
                    if security.check_password(buf):
                        self.send("OK")
                        self.state = PASSWORD_VERIFIED
                    else:
                        self.send("ERROR")
                        self.state = BLOCKED
                    self.input_password = ""
            elif (self.state == PASSWORD_VERIFIED):
                self.handleCommand(message)
            elif (self.state == BLOCKED):
                return
            else: #par défaut : BLOCKED, on ne répond plus
                return
        else:
            utils.trace("BLE : event reveived, " + str(event))

    def handleCommand(self,message):
        self.msg += message
        if(config.getValue(config._cmd_ble_end_char) in self.msg):
            spl = self.msg.split(config.getValue(config._cmd_ble_end_char))
            for completeCmd in spl:
                for key in self.commands.commands.keys():
                    if key in completeCmd:
                        args = completeCmd.split(config.getValue(config._cmd_separator))
                        res = None
                        error = False
                        if len(args) > 1:
                            argv = args[1]
                            cnt = len(args)
                            for i in range(2, cnt):
                                argv += config.getValue(config._cmd_separator) + args[i]
                            try:
                                res = self.commands.commands[key].execute(args[1])
                            except:
                                error = True
                        else:
                            try:
                                res = self.commands.commands[key].execute(None)
                            except:
                                error = True
                        if res is not None:
                            self.send(res)   
                            res = ""
                        else:
                            if error:
                                self.send("ERROR")
                            else:
                                self.send("OK")
            self.msg = spl[len(spl)-1]
    def register(self):
        # Nordic UART Service (NUS)
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
        BLE_NUS = bluetooth.UUID(NUS_UUID)
        BLE_RX = (bluetooth.UUID(RX_UUID), bluetooth.FLAG_WRITE)
        BLE_TX = (bluetooth.UUID(TX_UUID), bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY)
        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART, )
        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(SERVICES)
#         HR_UUID = bluetooth.UUID(0x180D)
#         HR_CHAR = (bluetooth.UUID(0x2A37), bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,)
#         HR_SERVICE = (HR_UUID, (HR_CHAR,), )
#         SERVICES = (BLE_UART, HR_SERVICE)
#         ((self.tx, self.rx,), (self.hr,), ) = self.ble.gatts_register_services(SERVICES)

    def send(self, data):
        for line in str(data).split("\n"):
            redo = True
            while redo:
                try:
                    self.ble.gatts_write(self.tx, str(line) + "\n")
                    self.ble.gatts_notify(self.conn_handle, self.tx )
                    redo = False
                except:
                    redo = True
                    time.sleep(0.1)

    def startAdvertise(self):
        name = bytes(self.name, 'UTF-8')
        self.ble.gap_advertise(100, bytearray('\x02\x01\x02') + bytearray((len(name) + 1, 0x09)) + name)
        
    def stopAdvertise(self):
        name = bytes(self.name, 'UTF-8')
        self.ble.gap_advertise(None, bytearray('\x02\x01\x02') + bytearray((len(name) + 1, 0x09)) + name)