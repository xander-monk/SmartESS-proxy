# SmartESS-proxy
SmartESS (PowMr) to MQTT proxy

## Overview
This project creates a proxy service that enables PowMr WiFi Plug Pro devices to send data to Home Assistant (HASS) via MQTT while optionally maintaining SmartESS cloud connectivity. It works by intercepting communications meant for `ess.eybond.com` through DNS poisoning.

## Features
- Modbus server implementation for device communication
- MQTT integration with Home Assistant
- Configurable update frequency
- Optional MQTT authentication
- Fake client mode to prevent cloud data transmission
- Multi-threaded operation
- Comprehensive logging with file rotation
- Error handling and recovery

## Prerequisites
- Python 3.7 or higher
- Network access to your PowMr device
- MQTT broker (like Mosquitto) for Home Assistant integration
- DNS configuration to redirect `ess.eybond.com` to your proxy

## Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/SmartESS-proxy.git
cd SmartESS-proxy
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration
Copy the sample configuration file to create your own:
```bash
cp conf.sample.ini conf.ini
```

Edit `conf.ini` with your settings. The sample configuration file includes detailed comments explaining each option.

Example configuration:
```ini
[DEFAULT]
fakeClient=true
mqttServer=172.16.2.1
mqttPort=1883
enableMqttAuth=false
mqttUser=
mqttPass=
mqttTopic=paxyhome/Inverter/
updateFrequency=10
```

### Configuration Options
- `fakeClient`: Set to true to prevent data from being sent to SmartESS cloud
- `mqttServer`: IP address or hostname of your MQTT broker
- `mqttPort`: MQTT broker port (default: 1883)
- `enableMqttAuth`: Set to true if your MQTT broker requires authentication
- `mqttUser`: MQTT username (if authentication is enabled)
- `mqttPass`: MQTT password (if authentication is enabled)
- `mqttTopic`: Base MQTT topic for publishing data
- `updateFrequency`: Data update frequency in seconds

## Usage
1. Configure your DNS to redirect `ess.eybond.com` to your proxy's IP address
2. Start the proxy:
```bash
python engine.py
```

The proxy will create a log file `smartess_proxy.log` with detailed operation information.

## Architecture
The project consists of several key components:
- `engine.py`: Main orchestrator that initializes and manages all components
- `modbus_server.py`: Implements Modbus server functionality
- `modbus_client.py`: Handles Modbus client operations
- `mqtt_client.py`: Manages MQTT communication
- `process_inverter_data.py`: Processes and transforms inverter data
- `fake_client.py`: Simulates client behavior for cloud-free operation

## Testing
Run the test suite:
```bash
python -m unittest discover tests
```

Individual test files can be run separately:
```bash
python -m unittest tests/test_data_extract.py
```
```bash
python -m unittest tests/test_engine.py
```

## Troubleshooting
1. Check the `smartess_proxy.log` file for detailed error messages and operation logs
2. Verify your network configuration and DNS settings
3. Ensure your MQTT broker is running and accessible
4. Confirm the PowMr device is on the same network

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.