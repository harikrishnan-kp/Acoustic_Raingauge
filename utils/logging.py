import logging
from os import path
from datetime import datetime

from utils.dir import get_logs_dir


def initialize_logging(audio_log_filename, start_time, total_samples):
    logging.basicConfig(
        filename=path.join(get_logs_dir(), audio_log_filename),
        filemode="a+",
        format="%(message)s",
    )
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info("*******************************************************")
    logger.info(f"Started data logging at {start_time}\n")
    logger.info(f"Total number of samples to be recorded: {total_samples}\n")
    return logger


def log_time_remaining(logger, end_time):
    time_left = end_time - datetime.now()
    days = time_left.days
    hours, remainder = divmod(time_left.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    log_message = f"Time left: {days} days {hours} hours {minutes} minutes and {seconds} seconds\n"
    logger.info(log_message)


def write_rain_data_to_csv(result_data, rain_log_filename):
    result_df = pd.DataFrame(result_data)
    result_df.to_csv(path.join(get_logs_dir(), rain_log_filename), index=False)