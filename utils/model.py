import os

from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, LSTM, Dense, Reshape, Input

from .helper import config
from .dir import get_weights_dir


def load_estimate_model(weight_file: str) -> any:
    """
    Loads deep learning model, build it and loads weights
    """
    weight = os.path.join(get_weights_dir, weight_file)
    model = create_lstm_model_withcnn()
    model.build(input_shape=config["stft_shape"])
    model.load_weights(weight)
    return model

def create_lstm_model_withcnn() -> any:
    """
    Creates and returns LSTM models with Conv and Dense blocks
    """
    model = Sequential()
    model.add(Input((1025, 2672, 1)))
    model.add(Conv2D(64, kernel_size=(8, 8), activation="relu"))
    model.add(MaxPooling2D(pool_size=(8, 8)))
    model.add(Conv2D(32, kernel_size=(4, 4), activation="relu"))
    model.add(MaxPooling2D(pool_size=(4, 4)))
    model.add(Conv2D(16, kernel_size=(2, 2), activation="relu"))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Reshape((1, -1)))
    model.add(LSTM(20))
    model.add(Dense(32))
    model.add(Dense(16))
    model.add(Dense(1))
    return model