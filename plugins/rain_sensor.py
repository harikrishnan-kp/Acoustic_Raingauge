import time

import RPi.GPIO as GPIO

from ..utils.helper import load_config


class RainSensor:
    def __init__(self, config="config.yaml"):
        config = load_config(config)
        self.power_pin = config["rain_sensor_power_pin"]
        self.rain_pin = config["rain_sensor_input_pin"]
        self._setup_gpio()

    def _setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.power_pin, GPIO.OUT)
        GPIO.setup(self.rain_pin, GPIO.IN)

    def _enable(self):
        GPIO.output(self.power_pin, GPIO.HIGH)

    def _disable(self):
        GPIO.output(self.power_pin, GPIO.LOW)

    def _read(self):
        return GPIO.input(self.rain_pin)

    def get_data(self):
        """
        Read rain sensor and return status.

        Returns:
            int: GPIO.HIGH if no rain detected,
                 GPIO.LOW if rain detected.
        """
        self._enable()
        time.sleep(0.01)
        rain_status = self._read()
        self._disable()

        return rain_status

    def is_raining(self):
        return self.get_data() == GPIO.LOW

    def cleanup(self):
        GPIO.cleanup([self.power_pin, self.rain_pin])


if __name__ == "__main__":
    rain_sensor = RainSensor()

    try:
        while True:
            if rain_sensor.is_raining():
                print("Rain detected")
            else:
                print("No rain detected")
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    finally:
        rain_sensor.cleanup()