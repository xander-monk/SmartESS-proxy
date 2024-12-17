class ModbusClient:
    def __init__(self, engine):
        self.engine = engine

    def run(self):
        raise NotImplementedError("Subclasses must implement run()")

    def send_data(self, data):
        raise NotImplementedError("Subclasses must implement send_data()")
