import logging
import math

import pyaudio

from shared import GracefulKiller


class AudioProvider(GracefulKiller):
    DEFAULT_CHANNELS = 1

    DEFAULT_DTYPE = pyaudio.paInt32

    def __init__(self, device_index=None, sample_rate=None, chunk_size=None, channels=None):
        self.p = pyaudio.PyAudio()
        self.device_index: int = device_index if device_index is not None else self.p.get_default_input_device_info()[
            'index']
        self.sample_rate: int = sample_rate if sample_rate is not None else self.detect_sample_rate()
        self.chunk_size: int = chunk_size if chunk_size is not None else self.detect_chunk_size()
        self.channels: int = channels if channels is not None else AudioProvider.DEFAULT_CHANNELS
        self.dtype = AudioProvider.DEFAULT_DTYPE
        self.stream: pyaudio.Stream = self.setup_stream()
        self.time_between_chunks: float = self.sample_rate / self.chunk_size

    def delete(self):
        self.stream.close()


    def detect_sample_rate(self) -> int:
        detected_sample_rate = self.p.get_device_info_by_index(self.device_index)['defaultSampleRate']
        if detected_sample_rate.is_integer():
            return int(detected_sample_rate)
        else:
            return int(math.floor(detected_sample_rate))

    def detect_chunk_size(self) -> int:
        # TODO Operation to adjust to updates per second
        logging.debug(f"Detected sample rate: {self.sample_rate}")
        return self.detect_sample_rate()

    def setup_stream(self) -> pyaudio.Stream:
        logging.debug(
            f"Setting up audio stream for device {self.device_index}: {self.p.get_device_info_by_index(self.device_index)}")
        return self.p.open(
            format=self.dtype,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            input_device_index=self.device_index
        )

    def get_next_bytes_of_stream(self):
        return self.stream.read(self.chunk_size)

    def get_time_between_chunks(self):
        pass

    @staticmethod
    def list_devices():
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            print(p.get_device_info_by_index(i))

    list_devices = staticmethod(list_devices)
