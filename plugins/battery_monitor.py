import sys
import serial
import struct
import time


class BatteryMonitoring:
    def __init__(self, port="/dev/ttyS0", baudrate=9600):
        self.ser = self.setup_serial_connection(port, baudrate)

    def setup_serial_connection(self, port, baudrate, timeout=1):
        try:
            ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
            return ser
        except serial.SerialException as e:
            print(f"Error setting up serial connection: {e}")
            sys.exit(1)

    def read_uint8(self):
        try:
            byte = self.ser.read(1)
            if byte:
                value = struct.unpack("B", byte)[0]  # Use "B" for unsigned 8-bit integer
                return value
            else:
                return None
        except Exception as e:
            print(f"Error reading from serial: {e}")
            return None

    def process_data(self, values):
        if len(values) == 4:
            solar_v = values[0] / 10.0
            battery_v = values[1] / 10.0
            solar_i = values[2] / 10.0
            battery_charging_i = values[3] / 10.0
            return solar_v, battery_v, solar_i, battery_charging_i
        else:
            print(f"Unexpected number of values: {len(values)}")
            return None, None, None, None

    def get_dataframe(self):
        values = []

        # Read data until start marker (21) is found
        while True:
            value = self.read_uint8()
            if value == 21:
                break

        # Read the next four values after 21
        for _ in range(4):
            value = self.read_uint8()
            if value is not None:
                values.append(value)

        # Read until end marker (75) is found
        while True:
            value = self.read_uint8()
            if value == 75:
                break

        # Process and return the values
        return self.process_data(values)


if __name__ == "__main__":
    battery_monitor = BatteryMonitoring()

    while True:
        solar_v, battery_v, solar_i, battery_charging_i = battery_monitor.get_dataframe()

        if solar_v is not None:
            print(f"Solar Voltage: {solar_v:.1f} V")
            print(f"Battery Voltage: {battery_v:.1f} V")
            print(f"Solar Current: {solar_i:.1f} A")
            print(f"Battery charging Current: {battery_charging_i:.1f} A")
        else:
            print("No valid data received.")

        time.sleep(1)  # Adjust as needed
