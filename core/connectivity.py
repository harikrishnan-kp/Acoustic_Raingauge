import subprocess

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from requests.exceptions import ConnectionError

from utils.helper import config, load_config


class Connectivity:
    def __init__(self, device_type: str):
        self.device_name = config[device_type]["name"]
        self.device_location = config[device_type]["location"]
        self.communication = config[device_type]["communication"]
        self.lorawan_cfg = config[device_type]["lorawan"]
        self.influxdb_cfg = config[device_type]["influxdb"]

        if self.communication == "LORAWAN":
            self.setup_lorawan_txn()
        else:
            self.setup_infludb_txn()

    def setup_lorawan_txn(self):
        self.dev_addr = self.lorawan_cfg["dev_addr"]
        self.nwk_skey = self.lorawan_cfg["nwk_skey"]
        self.app_skey = self.lorawan_cfg["app_skey"]
        self.led_flag = self.lorawan_cfg["led_flag"]

    def setup_infludb_txn(self):
        url = self.influxdb_cfg["url"]
        org = self.influxdb_cfg["org"]
        bucket = self.influxdb_cfg["bucket"]
        token = self.influxdb_cfg["token"]

        # creating an object of influxdb_client
        self.client = influxdb_client.InfluxDBClient(
            url=url, token=token, org=org, timeout=30_000
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def send_to_influxdb(self, data, solar_V, battery_V, solar_I, battery_I: float) -> bool:
        """
        Write data directly to influxDB
        """
        try:
            p = (
                influxdb_client.Point("acoustic raingauge")
                .tag("location", self.device_location)
                .field("rain", data)
                .field("solar voltage", solar_V)
                .field("battery voltage", battery_V)
                .field("solar current", solar_I)
                .field("battery current", battery_I)
            )

            self.write_api.write(bucket=bucket, org=org, record=p)
            client.close()
            return True
        except Exception as e:
            print(f"InfluxDB writing failed: {e}")
            return False

    def send_to_chirpstack(self, data, solar_V, battery_V, solar_I, battery_I):
        """
        send data to chirpstack via LoRaWAN
        """
        success = False
        while not success:
            try:
                result = subprocess.call(
                    [
                        "ttn-abp-send",
                        self.dev_addr,
                        self.nwk_skey,
                        self.app_skey,
                        str(data),
                        str(solar_V),
                        str(battery_V),
                        str(solar_I),
                        str(battery_I),
                        str(self.led_flag),
                    ]
                )

                if result == 0:
                    success = True
                else:
                    print("Subprocess call failed, retrying...")
            except subprocess.CalledProcessError as e:
                print(f"Error during subprocess call: {e}. Retrying...")

    def send_data(self, data, solar_V, battery_V, solar_I, battery_I):
        if self.communication_mode == "LORAWAN":
            self.send_to_chirpstack(data, solar_V, battery_V, solar_I, battery_I)
        else:
            self.send_to_influxdb(data, solar_V, battery_V, solar_I, battery_I)