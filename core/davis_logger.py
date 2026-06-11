from os import path
from datetime import datetime
import csv

import RPi.GPIO as GPIO
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from requests.exceptions import ConnectionError

from utils.helper import load_config, time_stamp_fnamer
from utils.dir import create_folder, get_logs_dir
from utils.logging import save_csv


class DavisRainGauge:

    def __init__(self, interrupt_pin: int = 13, logging_interval: int = 180):
        self.dt_start = datetime.now()
        self.config = load_config("config.yaml")
        self.session_dir = path.join(get_logs_dir(), time_stamp_fnamer(self.dt_start))
        create_folder(self.session_dir)

        self.interrupt_pin = interrupt_pin
        self.logging_interval = logging_interval

        self.Bucket_size_mm = 0.2
        self.count = 0
        self.count_lock = threading.Lock()
        self._setup_gpio()

    def _setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(interrupt_pin, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
        GPIO.add_event_detect(interrupt_pin, GPIO.RISING, callback=bucket_tipped, bouncetime=50)

    def reset_count(self):
        with self.count_lock:
            self.count = 0
    
    def bucket_tipped(self, channel):
        with self.count_lock:
            self.count += 1
            
            # workaround for error tipps
            if self.count > 50:
                self.reset_count()

        print("Bucket Tipped")
    
    def write_influxdb(self, rain: float) -> bool:
        try:
            name = "rainpi_mech"
            location = "greenfield tvm"

            influxdb_config = load_config("influxdb_api.yaml")

            client = influxdb_client.InfluxDBClient(
                url=influxdb_config["url"],
                token=influxdb_config[name]["token"],
                org=influxdb_config["org"],
                timeout=30_000,
            )

            write_api = client.write_api(write_options=SYNCHRONOUS)
            point = (
                influxdb_client.Point("pi_davis_raingauge")
                .tag("location", location)
                .field("rain", rain)
            )

            write_api.write(
                bucket=influxdb_config[name]["bucket"],
                org=influxdb_config["org"],
                record=point,
            )

            client.close()
            return True

        except ConnectionError as exc:
            print(f"Connection failed: {exc}")
            return False

    def calculate_rainfall(self):
        with self.count_lock:
            return self.count * self.Bucket_size_mm

    def run(self):
        next_log_time = datetime.now() + timedelta(seconds=self.logging_interval)

        try:
            while True:
                now = datetime.now()
                if now >= next_log_time:
                    rainfall = self.calculate_rainfall()
                    self.reset_count()
                    self.write_influxdb(rainfall)
                    save_csv(now, rainfall, self.config["davis_log_filename"], self.session_dir)
                    next_log_time += timedelta(seconds=self.logging_interval)
                    
        except KeyboardInterrupt:
            print("Stopping rain gauge")

        finally:
            GPIO.cleanup()


if __name__ == "__main__":
    DavisRainGauge().run()
