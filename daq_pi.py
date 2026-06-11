from os import path, listdir
from datetime import datetime, timedelta
import threading

import pandas as pd

from plugins import BatteryMonitor, MoistureSensor
from core.model import RainfallEstimator
from core.davis_logger import DavisRainGauge
from core.connectivity import send_data
from utils.helper import time_stamp_fnamer, delete_files, config
from utils.logging import initialize_logging, log_time_remaining, write_rain_data_to_csv
from utils.dir import get_data_dir
from utils.audio_rec import record_audio


class AcousticRaingauge:

    def __init__(self):
        self.DB_write_interval = config["DB_writing_interval_min"]
        self.num_subsamples = config["infer_inetrval_sec"] // config["sample_duration_sec"]
        self.record_hours = config["record_hours"]
        self.end_time = datetime.now() + timedelta(hours=self.record_hours)
        self.moisture_threshold = config["field_deployed"]
        self.min_threshold = config["min_threshold"]
        self.moisture_threshold = config["moisture_threshold"]

        self.acoustic_model = RainfallEstimator()
        self.battery = BatteryMonitor()
        self.moisture_sensor = MoistureSensor()

    def run(self):
        db_counter, rain = 0, 0
        locations = []
        result_data = []
        data_dir = get_data_dir()

        try:
            if self.moisture_threshold:
                i = 1 # audio sample number
                while True:
                    dt_now = datetime.now()
                    print(f"Recording sample number {i} on {dt_now}")
                    audio_fname = time_stamp_fnamer(dt_now) + ".wav"
                    location = path.join(data_dir, audio_fname)
                    record_audio(
                        location,
                        config["sample_duration_sec"],
                        config["file_format"],
                        config["resolution"],
                        config["sampling_rate"],
                    )
                    locations.append(location)

                    if i % self.num_subsamples == 0: # if (infer_inetrval // wav_duration) no of audio subsamples are collected
                        mm_hat = self.acoustic_model.estimate_rainfall(locations) # estimating rainfall
                        print("Estimated rainfall: ", mm_hat)

                        files_and_directories = listdir(data_dir)
                        files_to_delete = [
                            path.join(data_dir, f)
                            for f in files_and_directories
                            if path.isfile(path.join(data_dir, f))
                        ]

                        delete_files(files_to_delete)
                        locations.clear()

                        rain += mm_hat
                        db_counter += 1

                        # reading moisture sensor
                        moisture = moisture_sensor.get_data()

                        # reading battery parameters
                        # solar_V, battery_V, solar_I, battery_I = 17.2, 15.2, 1.5, 2.2
                        solar_V, battery_V, solar_I, battery_I = (self.battery.get_dataframe())

                        # sending data to DB
                        if db_counter == self.DB_write_interval:
                            if moisture and moisture < self.moisture_threshold and rain >= self.min_threshold:
                                send_data(config, mm_hat, solar_V, battery_V, solar_I, battery_I)
                            else:
                                send_data(config, 0.0, solar_V, battery_V, solar_I, battery_I)
                            rain, db_counter = 0, 0
                    i += 1

            else:
                # run mechanical raingauge in new thread
                mech_raingauge = DavisRainGauge()
                rain_thread = threading.Thread(target=mech_raingauge.run, daemon=True).start()

                logger = initialize_logging(
                    config["audio_log_filename"],
                    datetime.now(),
                    int(self.record_hours * (3600 / config["sample_duration_sec"])),
                )
                for i in range(1, int(self.record_hours * (3600 / config["sample_duration_sec"])) + 1):
                    dt_now = datetime.now()
                    logger.info(f"Recording sample number {i} on {dt_now}")
                    audio_fname = time_stamp_fnamer(dt_now) + ".wav"
                    location = path.join(data_dir, audio_fname)
                    record_audio(
                        location,
                    config["sample_duration_sec"],
                        config["file_format"],
                        config["resolution"],
                        config["sampling_rate"],
                    )
                    locations.append(location)

                    if i % self.num_subsamples == 0: # estimating rainfall
                        mm_hat = self.acoustic_model.estimate_rainfall(locations)
                        # logger.info("Estimated rainfall: ", mm_hat)
                        locations.clear()
                        moisture = moisture_sensor.get_data() # reading moisture sensor
                        result_data.append(
                            {
                                "time_stamp": dt_now,
                                "rainfall_estimate": mm_hat,
                                "moisture": moisture,
                            }
                        )
                        write_rain_data_to_csv(result_data, config["rain_log_filename"])
                        rain += mm_hat
                        db_counter += 1

                        # reading battery parameters
                        # solar_V, battery_V, solar_I, battery_I = 17.2, 15.2, 1.5, 2.2
                        solar_V, battery_V, solar_I, battery_I = (self.battery.get_dataframe())
                        
                        # sending data to DB
                        if db_counter == self.DB_write_interval:
                            if moisture and moisture < self.moisture_threshold and rain >= self.min_threshold:
                                send_data(config, mm_hat, solar_V, battery_V, solar_I, battery_I)

                            else:
                                send_data(config, 0.0, solar_V, battery_V, solar_I, battery_I)
                            rain, db_counter = 0, 0
                    log_time_remaining(logger, self.end_time)
                logger.info(f"Finished data logging at {datetime.now()}\n")

        except KeyboardInterrupt:
            print("Execution interrupted by user")
        finally:
            pass


if __name__ == "__main__":
    AcousticRaingauge.run()
