import unittest
import os
import configparser
from unittest.mock import MagicMock, patch
from engine import Engine

class TestEngine(unittest.TestCase):
    def setUp(self):
        # Create a temporary config file for testing
        self.config = configparser.ConfigParser()
        self.config['DEFAULT'] = {
            'fakeClient': 'true',
            'mqttServer': 'test.mosquitto.org',
            'mqttPort': '1883',
            'enableMqttAuth': 'false',
            'mqttUser': '',
            'mqttPass': '',
            'mqttTopic': 'test/inverter/',
            'updateFrequency': '10'
        }
        with open('test_conf.ini', 'w') as configfile:
            self.config.write(configfile)

    def tearDown(self):
        # Clean up temporary config file
        if os.path.exists('test_conf.ini'):
            os.remove('test_conf.ini')
        if os.path.exists('smartess_proxy.log'):
            os.remove('smartess_proxy.log')

    @patch('engine.ModbusServer')
    @patch('engine.FakeClient')
    @patch('engine.MQTTClient')
    def test_engine_initialization(self, mock_mqtt, mock_fake_client, mock_modbus_server):
        """Test that Engine initializes all components correctly"""
        engine = Engine()
        
        # Verify that all components were initialized
        self.assertIsNotNone(engine.pool)
        mock_modbus_server.assert_called_once()
        mock_fake_client.assert_called_once()
        mock_mqtt.assert_called_once()

    def test_config_loading(self):
        """Test that configuration is loaded correctly"""
        engine = Engine()
        
        # Verify default values
        self.assertTrue(engine.fake_client)
        self.assertEqual(engine.mqtt_server, "172.16.2.1")
        self.assertEqual(engine.mqtt_port, 1883)
        self.assertFalse(engine.enable_mqtt_auth)
        self.assertEqual(engine.mqtt_topic, "paxyhome/Inverter/")
        self.assertEqual(engine.fake_client_update_frequency, 10)

    def test_hex_string_conversion(self):
        """Test hex string to byte array conversion"""
        test_hex = "48656C6C6F"  # "Hello" in hex
        result = Engine.hex_string_to_byte_array(test_hex)
        self.assertEqual(result, b'Hello')

    @patch('engine.ModbusServer')
    @patch('engine.ModbusClient')
    @patch('engine.MQTTClient')
    def test_real_client_mode(self, mock_mqtt, mock_modbus_client, mock_modbus_server):
        """Test engine initialization in real client mode"""
        # Create config with fake_client = False
        config = configparser.ConfigParser()
        config['DEFAULT'] = {
            'fakeClient': 'false',
            'mqttServer': 'test.mosquitto.org',
            'mqttPort': '1883'
        }
        with open('conf.ini', 'w') as configfile:
            config.write(configfile)

        engine = Engine()
        
        # Verify that ModbusClient was used instead of FakeClient
        mock_modbus_client.assert_called_once()
        mock_mqtt.assert_called_once()

if __name__ == '__main__':
    unittest.main()
