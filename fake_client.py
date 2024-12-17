import threading
import time
from datetime import datetime
from modbus_client import ModbusClient

class FakeClient(ModbusClient):
    CFG = "3D0A0001000EFF020102030405080C0E191A2041"
    PING = "3D0B0001000AFF011609190F00350023"
    GET_DATA = "3D0C00010003001100"

    def __init__(self, engine):
        super().__init__(engine)
        self.engine = engine
        self.srv = None

    def run(self):
        while True:
            try:
                self.send_msg_to_client(self.CFG)
                while True:
                    res = self.send_msg_to_client(self.GET_DATA)
                    if res == -1:
                        break
                    time.sleep(self.engine.fake_client_update_frequency)
            except Exception as e:
                print(f"Error in FakeClient: {e}")

    def send_data(self, data):
        return 0

    def send_msg_to_client(self, msg):
        while self.engine.nsrv is None or self.engine.nsrv.node is None:
            time.sleep(0.1)
        
        data = bytes.fromhex(msg)
        res = self.engine.nsrv.send_data(data)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(f"{current_time} - Server: {msg}")
        return res
