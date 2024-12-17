import time
import struct

class ProcessInverterData:
    def __init__(self, engine):
        self.engine = engine
        # Data indices
        self.mode_idx = 14
        self.ac_voltage_idx = 16
        self.ac_frequency_idx = 18
        self.pv_voltage_idx = 20
        self.pv_power_idx = 22
        self.battery_voltage_idx = 24
        self.battery_charged_idx = 26
        self.battery_charging_curr_idx = 28
        self.battery_discharging_curr_idx = 30
        self.output_voltage_idx = 32
        self.output_frequency_idx = 34
        self.output_power_idx = 38
        self.output_load_idx = 40
        self.charge_state_idx = 84
        self.load_state_idx = 86

    def run(self):
        while True:
            try:
                # Wait for data to be available
                while self.engine.last_data is None or len(self.engine.last_data) == 0:
                    time.sleep(0.1)
                
                data = self.engine.last_data
                hex_data = data.hex()

                # Process data type 0x0925
                if data[2] == 0x09 and data[3] == 0x25:
                    self._process_status_data(data)
                
                # Process data type 0x0001
                if data[2] == 0x00 and data[3] == 0x01:
                    self._process_command_response(hex_data)

                self.engine.last_data = None

            except Exception as e:
                print(f"Error processing inverter data: {e}")

    def _process_status_data(self, data):
        """Process the status data packet (type 0x0925)"""
        # Battery data
        battery_voltage = self._get_data(data, self.battery_voltage_idx, 10)
        self.engine.mqtt.send_msg("batteryVoltage", battery_voltage)
        
        battery_charged = self._get_data_int(data, self.battery_charged_idx)
        self.engine.mqtt.send_msg("batteryCharged", battery_charged)
        
        battery_charging_curr = self._get_data(data, self.battery_charging_curr_idx, 10)
        self.engine.mqtt.send_msg("batteryChargingCurr", battery_charging_curr)
        
        battery_discharging_curr = self._get_data(data, self.battery_discharging_curr_idx, 10)
        self.engine.mqtt.send_msg("batteryDisChargingCurr", battery_discharging_curr)

        # Output data
        output_voltage = self._get_data(data, self.output_voltage_idx, 10)
        self.engine.mqtt.send_msg("outputVoltage", output_voltage)
        
        output_frequency = self._get_data(data, self.output_frequency_idx, 10)
        self.engine.mqtt.send_msg("outputFrequency", output_frequency)
        
        output_power = self._get_data_int(data, self.output_power_idx)
        self.engine.mqtt.send_msg("outputPower", output_power)
        
        output_load = self._get_data_int(data, self.output_load_idx)
        self.engine.mqtt.send_msg("outputLoad", output_load)

        # AC data
        ac_voltage = self._get_data(data, self.ac_voltage_idx, 10)
        self.engine.mqtt.send_msg("acVoltage", ac_voltage)
        
        ac_frequency = self._get_data(data, self.ac_frequency_idx, 10)
        self.engine.mqtt.send_msg("acFrequency", ac_frequency)

        # PV data
        pv_voltage = self._get_data(data, self.pv_voltage_idx, 10)
        self.engine.mqtt.send_msg("pvVoltage", pv_voltage)
        
        pv_power = self._get_data_int(data, self.pv_power_idx)
        self.engine.mqtt.send_msg("pvPower", pv_power)

        # Mode and state data
        mode = self._get_data_int(data, self.mode_idx)
        self.engine.mqtt.send_msg("mode", mode)
        
        charge_state = self._get_data_int(data, self.charge_state_idx)
        self.engine.mqtt.send_msg("chargeState", charge_state)
        
        load_state = self._get_data_int(data, self.load_state_idx)
        self.engine.mqtt.send_msg("loadState", load_state)

    def _process_command_response(self, hex_data):
        """Process command response data (type 0x0001)"""
        charge_state = -1
        load_state = -1

        # Compare with known command responses
        if hex_data == self.engine.mqtt.CHARGE_SOLAR_ONLY:
            charge_state = 3
        elif hex_data == self.engine.mqtt.CHARGE_SOLAR_UTILITY:
            charge_state = 2
        elif hex_data == self.engine.mqtt.LOAD_SBU:
            load_state = 2
        elif hex_data == self.engine.mqtt.LOAD_UTILITY:
            load_state = 0

        if charge_state != -1:
            self.engine.mqtt.send_msg("chargeState", charge_state)
        if load_state != -1:
            self.engine.mqtt.send_msg("loadState", load_state)

    def _get_data(self, data, idx, denominator):
        """Get float data from byte array"""
        value = self._get_bytes_as_int(data[idx:idx+2])
        return value / denominator

    def _get_data_int(self, data, idx):
        """Get integer data from byte array"""
        return self._get_bytes_as_int(data[idx:idx+2])

    @staticmethod
    def _get_bytes_as_int(bytes_data):
        """Convert 2 bytes to integer in big-endian format"""
        return int.from_bytes(bytes_data[::-1], byteorder='big', signed=False)
