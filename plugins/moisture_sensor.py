"""
Enable I2C in sudo raspi-config and reboot
Check I2C with the command : i2cdetect -y 1

connection
ADC  Module: ADS1115
VDD - 5V
GND - GND
SCL - SCL.1 (Physical 5)
SDA - SDA.1 (Physical 3)
ADDR - GND
A0 - Grove moisture Sensor output 
"""
import time

from Adafruit_ADS1x15 import ADS1115


class MoistureSensor:
    def __init__(self, channel=0, gain=1):
        self.adc = ADS1115()
        self.channel = channel
        self.gain = gain

    def get_data(self):
        return self.adc.read_adc(self.channel, self.gain)


if __name__ == "__main__":
    sensor = MoistureSensor()
    while True:
        value = sensor.get_data()
        if value is not None:
            print(f"Raw value: {value}")
        else:
            print(f"Cannot read moisture sensor {value}")
        time.sleep(0.2)
