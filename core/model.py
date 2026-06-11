import os

import librosa
import numpy as np
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, LSTM, Dense, Reshape, Input

from utils.helper import config
from utils.dir import get_weights_dir


class RainfallEstimator:
    def __init__(self):
        self.model = self.load_model(config["infer_model_name"])

    def load_model(self, weight_file: str):
        """
        Loads deep learning model, build it and loads weights
        """
        weight = os.path.join(get_weights_dir, weight_file)
        model = lstm_withcnn()
        model.build(input_shape=config["stft_shape"])
        model.load_weights(weight)
        return model

    @staticmethod
    def lstm_withcnn():
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

    def combine_audios(self, file_paths: list) -> np.ndarray:
        """
        Combines various audio files in their chronological order
        based on list of audio file paths provided
        """
        audio = np.array([])
        for file_path in file_paths:
            audio_segment, _ = librosa.load(file_path, sr=int(config["sampling_rate"]))
            audio = np.append(audio, audio_segment)
        return audio

    def extract_stft(self, raw_data: np.ndarray) -> np.ndarray:
        """
        Calculates and returns STFT on raw input audio provided
        """
        Zxx = librosa.stft(raw_data)
        stft_sample = np.abs(Zxx)
        return stft_sample[np.newaxis, :, :]

    def estimate_rainfall(self, file_paths: list) -> float:
        """
        Computed the models prediction on input data provided
        """
        audio = self.combine_audios(file_paths)
        audio = audio[: config["seq_len"]]
        stft_sample = self.extract_stft(audio)
        y_pred = self.model.predict(stft_sample, verbose=0)[0][0]
        return y_pred
