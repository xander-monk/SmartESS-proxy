import unittest
from process_inverter_data import ProcessInverterData

class TestDataExtract(unittest.TestCase):
    def setUp(self):
        # Initialize indices as in the original code
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

        # Test data
        self.test_hex = "2B270925008205110000119511D10400CE08F301B90001007C00420000000000CE08F301100000000100010072B20000C1A200000100DC05DC05E60006007800E600F401060000000000F9231601D70F72006501020001000000020000003C00E6001E00740087007E007D0064008D003C0078001E0062ECE90E010000004A000000000000000000"
        self.data = bytes.fromhex(self.test_hex)

    def test_data_extraction(self):
        """Test extraction of all data fields from the test hex string"""
        # Verify packet type
        self.assertEqual(self.data[2], 0x09)
        self.assertEqual(self.data[3], 0x25)

        # Test all data extractions
        test_cases = [
            ("batteryVoltage", self.battery_voltage_idx, 10, False),
            ("batteryCharged", self.battery_charged_idx, 1, True),
            ("batteryChargingCurr", self.battery_charging_curr_idx, 10, False),
            ("batteryDisChargingCurr", self.battery_discharging_curr_idx, 10, False),
            ("outputVoltage", self.output_voltage_idx, 10, False),
            ("outputFrequency", self.output_frequency_idx, 10, False),
            ("outputPower", self.output_power_idx, 1, True),
            ("outputLoad", self.output_load_idx, 1, True),
            ("acVoltage", self.ac_voltage_idx, 10, False),
            ("acFrequency", self.ac_frequency_idx, 10, False),
            ("pvVoltage", self.pv_voltage_idx, 10, False),
            ("pvPower", self.pv_power_idx, 1, True),
            ("mode", self.mode_idx, 1, True),
            ("chargeState", self.charge_state_idx, 1, True),
            ("loadState", self.load_state_idx, 1, True)
        ]

        for name, idx, denominator, is_int in test_cases:
            if is_int:
                value = self._get_data_int(self.data, idx)
                print(f"{name}: {value}")
            else:
                value = self._get_data(self.data, idx, denominator)
                print(f"{name}: {value}")

            # Add assertions here based on expected values
            self.assertIsNotNone(value)
            if is_int:
                self.assertIsInstance(value, int)
            else:
                self.assertIsInstance(value, float)

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

if __name__ == '__main__':
    unittest.main()
