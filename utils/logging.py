from __future__ import annotations

import logging
import sys
import os
from datetime import datetime

from utils.dir import get_logs_dir


class ColorFormatter(logging.Formatter):
    """Custom formatter with colored output."""

    COLORS = {
        logging.DEBUG: "\033[36m",  # Cyan
        logging.INFO: "\033[32m",  # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",  # Red
        logging.CRITICAL: "\033[41m",  # Red background
    }

    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    RESET = "\033[0m"

    def __init__(self, repo_name: str):
        super().__init__()
        self.repo_name = repo_name

    def format(self, record: logging.LogRecord) -> str:
        level_color = self.COLORS.get(record.levelno, "")
        level_name = record.levelname
        asctime = self.formatTime(record, "%Y-%m-%d %H:%M:%S")

        return (
            f"{asctime} "
            f"{self.MAGENTA}[{self.repo_name}]{self.RESET} "
            f"{level_color}[{level_name}]{self.RESET} "
            f"{self.BLUE}[{record.name}]{self.RESET} "
            f"{record.getMessage()}"
        )


def _resolve_log_level() -> int:
    """Return the numeric log level from the ``LOG_LEVEL`` env-var.

    Accepts both numeric strings (``"10"``) and level names (``"DEBUG"``).
    Falls back to ``logging.INFO`` when the variable is unset or invalid.
    """

    env = os.environ.get("LOG_LEVEL", "").strip().upper()
    if not env:
        return logging.INFO

    # Try numeric first, then name-based lookup.
    try:
        return int(env)
    except ValueError:
        return getattr(logging, env, logging.INFO)


def configure_logging(
    *, level: int | None = None, repo_name: str = "Acoustic Raingauge"
) -> None:
    """Configure application logging.

    When *level* is ``None`` the ``LOG_LEVEL`` environment variable is
    consulted; if that is also unset the default ``logging.INFO`` is used.
    """

    if level is None:
        level = _resolve_log_level()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColorFormatter(repo_name))

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Prevent duplicate handlers when configure_logging()
    # is called multiple times.
    root_logger.handlers.clear()
    root_logger.addHandler(handler)


def initialize_logging(audio_log_filename, start_time, total_samples):
    logging.basicConfig(
        filename=os.path.join(get_logs_dir(), audio_log_filename),
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
    result_df.to_csv(os.path.join(get_logs_dir(), rain_log_filename), index=False)


def save_csv(self, time, rain, file_name, session_dir):
    file_exists = os.path.isfile(os.path.join(session_dir, file_name))

    with open(csv_path, "a", newline="") as csv_file:
        writer = csv.writer(csv_file)

        if not file_exists:
            writer.writerow(["time", "rainfall"])

        writer.writerow([time, rain])