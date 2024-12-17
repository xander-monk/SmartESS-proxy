import configparser
import logging
import logging.handlers
from concurrent.futures import ThreadPoolExecutor
from modbus_server import ModbusServer
from fake_client import FakeClient
from modbus_client import ModbusClient
from mqtt_client import MQTTClient
from process_inverter_data import ProcessInverterData

def setup_logging():
    """Configure logging with both file and console handlers."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        'smartess_proxy.log', maxBytes=1024*1024, backupCount=5)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger

class Engine:
    def __init__(self):
        self.logger = setup_logging()
        self.logger.info("Initializing SmartESS Proxy Engine")
        # Default values
        self.fake_client = True
        self.mqtt_server = "172.16.2.1"
        self.enable_mqtt_auth = False
        self.mqtt_user = ""
        self.mqtt_pass = ""
        self.mqtt_port = 1883
        self.mqtt_topic = "paxyhome/Inverter/"
        self.fake_client_update_frequency = 10
        self.real_modbus_server = "47.242.188.205"
        
        self.pool = ThreadPoolExecutor(max_workers=4)
        self.nsrv = None
        self.ncli = None
        self.mqtt = None
        self.last_data = None
        
        self.load_config()
        self.initialize_components()

    def load_config(self):
        config = configparser.ConfigParser()
        try:
            config.read('conf.ini')
            settings = config['DEFAULT']
            
            self.fake_client = settings.getboolean('fakeClient', self.fake_client)
            self.mqtt_server = settings.get('mqttServer', self.mqtt_server)
            self.mqtt_port = settings.getint('mqttPort', self.mqtt_port)
            self.enable_mqtt_auth = settings.getboolean('enableMqttAuth', self.enable_mqtt_auth)
            self.mqtt_user = settings.get('mqttUser', self.mqtt_user)
            self.mqtt_pass = settings.get('mqttPass', self.mqtt_pass)
            self.mqtt_topic = settings.get('mqttTopic', self.mqtt_topic)
            self.fake_client_update_frequency = settings.getint('updateFrequency', self.fake_client_update_frequency)
            
            self.logger.info("Configuration loaded successfully")
            self.logger.debug(f"MQTT Server: {self.mqtt_server}:{self.mqtt_port}")
            self.logger.debug(f"MQTT Topic: {self.mqtt_topic}")
            self.logger.debug(f"Fake Client Mode: {self.fake_client}")
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            raise

    def initialize_components(self):
        try:
            self.logger.info("Initializing components...")
            # Initialize ModbusServer
            self.nsrv = ModbusServer(self)
            self.pool.submit(self.nsrv.run)
            self.logger.info("ModbusServer initialized")

            if self.fake_client:
                self.logger.info("Starting in Fake Client mode")
                self.ncli = FakeClient(self)
            else:
                self.logger.info("Starting in Real Client mode")
                self.ncli = ModbusClient(self)
            self.pool.submit(self.ncli.run)

            # Initialize MQTT Client
            self.mqtt = MQTTClient(self)
            self.pool.submit(self.mqtt.run)
            self.logger.info("MQTT Client initialized")

            # Initialize ProcessInverterData
            self.processor = ProcessInverterData(self)
            self.pool.submit(self.processor.run)

        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise

    @staticmethod
    def hex_string_to_byte_array(hex_string):
        """Convert hex string to byte array"""
        return bytes.fromhex(hex_string)

def main():
    try:
        engine = Engine()
        # Keep the main thread alive
        while True:
            try:
                import time
                time.sleep(1)
            except KeyboardInterrupt:
                print("\nShutting down...")
                break
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    main()
