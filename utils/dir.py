from pathlib import Path


def get_base_dir():
    return Path(__file__).resolve().parent.parent

def get_weights_dir():
    weights_dir = get_base_dir() / "weights"
    weights_dir.mkdir(parents=True, exist_ok=True)
    return weights_dir

def get_logs_dir():
    weights_dir = get_base_dir() / "logs"
    weights_dir.mkdir(parents=True, exist_ok=True)
    return weights_dir

def get_data_dir():
    weights_dir = get_base_dir() / "data"
    weights_dir.mkdir(parents=True, exist_ok=True)
    return weights_dir

def get_config_dir():
    weights_dir = get_base_dir() / "config"
    weights_dir.mkdir(parents=True, exist_ok=True)
    return weights_dir

def create_folder(directory: str) -> None:
    Path(directory).mkdir(parents=True, exist_ok=True)