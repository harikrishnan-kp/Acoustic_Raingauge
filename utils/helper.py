import yaml
from os import path,makedirs,remove
from .dir import get_config_dir


def load_config(config_name: str) -> dict:
    """
    A function to load and return config file in YAML format.
    """
    with open(path.join(get_config_dir(), config_name)) as file:
        config = yaml.safe_load(file)
    return config

def time_stamp_fnamer(tstamp) -> str:
    """
    A function to generate filenames from timestamps
    """
    cdate, ctime = str(tstamp).split(" ")
    current_date = "_".join(cdate.split("-"))
    chour, cmin, csec = ctime.split(":")
    csec, cmilli = csec.split(".")
    current_time = "_".join([chour, cmin, csec, cmilli])
    current_date_time_name = "_".join([current_date, current_time])
    return current_date_time_name

def delete_files(file_paths):
    """
    Function to delete wav files after inference
    """
    for file_path in file_paths:
        try:
            if path.exists(file_path):
                remove(file_path)
                print(f"Deleted: {file_path}")
            else:
                print(f"File does not exist: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")


# loading config files
config = load_config("config.yaml")