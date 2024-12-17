import paho.mqtt.client as mqtt
import json
import logging
import time
from threading import Event, Lock

class MQTTClient:
    # Command constants
    CHARGE_SOLAR_ONLY = "3D0A0001000EFF020102030405080C0E191A2041"
    CHARGE_SOLAR_UTILITY = "3D0B0001000AFF011609190F00350023"
    LOAD_SBU = "3D0C00010003001100"
    LOAD_UTILITY = "3D0D00010003001000"

    def __init__(self, engine):
        self.logger = logging.getLogger(__name__)
        self.engine = engine
        self.client = mqtt.Client()
        self.connected = False
        self.connect_lock = Lock()
        self.stop_event = Event()
        self.reconnect_delay = 1  # Start with 1 second delay
        self.max_reconnect_delay = 60  # Maximum delay of 60 seconds
        
        # Set up callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        
        # Configure authentication if enabled
        if self.engine.enable_mqtt_auth:
            self.client.username_pw_set(
                self.engine.mqtt_user,
                self.engine.mqtt_pass
            )
            self.logger.info("MQTT authentication configured")

    def on_connect(self, client, userdata, flags, rc):
        """Callback for when the client receives a CONNACK response from the server."""
        if rc == 0:
            self.logger.info("Successfully connected to MQTT broker")
            with self.connect_lock:
                self.connected = True
                self.reconnect_delay = 1  # Reset reconnect delay on successful connection
        else:
            self.logger.error(f"Failed to connect to MQTT broker with result code: {rc}")
            self.handle_connection_error(rc)

    def on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the server."""
        with self.connect_lock:
            self.connected = False
        if rc != 0:
            self.logger.warning(f"Unexpected MQTT disconnection with result code: {rc}")
        else:
            self.logger.info("MQTT client disconnected")

    def on_publish(self, client, userdata, mid):
        """Callback for when a message is published."""
        self.logger.debug(f"Message {mid} published successfully")

    def handle_connection_error(self, rc):
        """Handle different connection error scenarios."""
        error_messages = {
            1: "Incorrect protocol version",
            2: "Invalid client identifier",
            3: "Server unavailable",
            4: "Bad username or password",
            5: "Not authorized"
        }
        error_msg = error_messages.get(rc, f"Unknown error code: {rc}")
        self.logger.error(f"MQTT Connection Error: {error_msg}")
        
        if rc in [4, 5]:  # Auth related errors
            self.logger.critical("Authentication failed. Please check credentials.")
            self.stop_event.set()  # Stop reconnection attempts
        
    def connect_with_retry(self):
        """Attempt to connect to the MQTT broker with exponential backoff."""
        while not self.stop_event.is_set():
            try:
                self.logger.info(f"Attempting to connect to MQTT broker at {self.engine.mqtt_server}:{self.engine.mqtt_port}")
                self.client.connect(self.engine.mqtt_server, self.engine.mqtt_port)
                return True
            except Exception as e:
                self.logger.error(f"Failed to connect to MQTT broker: {str(e)}")
                self.logger.info(f"Retrying in {self.reconnect_delay} seconds...")
                self.stop_event.wait(self.reconnect_delay)
                
                # Implement exponential backoff
                self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
        return False

    def process_data(self, data):
        try:
            return {
                "raw_data": data.hex(),
                "timestamp": time.time()
            }
        except Exception as e:
            self.logger.error(f"Error processing data: {e}")
            return None

    def publish_data(self, data):
        """Publish data to MQTT broker with error handling."""
        if not self.connected:
            self.logger.warning("Not connected to MQTT broker. Attempting to reconnect...")
            if not self.connect_with_retry():
                self.logger.error("Failed to reconnect to MQTT broker")
                return False

        try:
            topic = f"{self.engine.mqtt_topic}data"
            message = json.dumps(data)
            result = self.client.publish(topic, message, qos=1)
            
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                self.logger.error(f"Failed to publish message: {mqtt.error_string(result.rc)}")
                return False
                
            self.logger.debug(f"Published data to {topic}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error publishing data: {str(e)}")
            return False

    def send_msg(self, topic, value):
        """Send a message to a specific MQTT topic"""
        try:
            full_topic = f"{self.engine.mqtt_topic}{topic}"
            self.client.publish(full_topic, str(value))
        except Exception as e:
            self.logger.error(f"Error sending message to {topic}: {e}")

    def run(self):
        """Main run loop for the MQTT client."""
        self.logger.info("Starting MQTT client...")
        
        if not self.connect_with_retry():
            self.logger.error("Failed to establish initial connection. Exiting.")
            return

        try:
            self.client.loop_start()
            
            while not self.stop_event.is_set():
                if not self.connected:
                    if not self.connect_with_retry():
                        break
                if self.engine.last_data:
                    try:
                        # Process and publish the data
                        data = self.process_data(self.engine.last_data)
                        if data:
                            self.publish_data(data)
                    except Exception as e:
                        self.logger.error(f"Error processing/publishing data: {e}")
                self.stop_event.wait(1)  # Check connection status every second
                
        except Exception as e:
            self.logger.error(f"Error in MQTT client run loop: {str(e)}")
        finally:
            self.logger.info("Shutting down MQTT client...")
            self.client.loop_stop()
            self.client.disconnect()

    def stop(self):
        """Gracefully stop the MQTT client."""
        self.logger.info("Stopping MQTT client...")
        self.stop_event.set()
