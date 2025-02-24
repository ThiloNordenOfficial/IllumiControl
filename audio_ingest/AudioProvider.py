import logging
import math

import pyaudio


class AudioProvider:
    p = pyaudio.PyAudio()
    DEFAULT_CHUNK_SIZE = 16384
    DEFAULT_CHANNELS = 1
    DEFAULT_DTYPE = pyaudio.paInt16

    def __init__(self, device_index: int, sample_rate=None, chunk_size=None, channels=None):
        self.device_index: int = device_index
        self.sample_rate: int = sample_rate if sample_rate is not None else self.detect_sample_rate()
        self.chunk_size: int = chunk_size if chunk_size is not None else AudioProvider.DEFAULT_CHUNK_SIZE
        self.channels: int = channels if channels is not None else AudioProvider.DEFAULT_CHANNELS
        self.dtype = AudioProvider.DEFAULT_DTYPE
        self.stream: pyaudio.Stream = self.setup_stream()

    def detect_sample_rate(self) -> int:
        detected_sample_rate = self.p.get_device_info_by_index(self.device_index)['defaultSampleRate']
        if detected_sample_rate.is_integer():
            return int(detected_sample_rate)
        else:
            return int(math.floor(detected_sample_rate))

    def setup_stream(self) -> pyaudio.Stream:
        return self.p.open(
            format=self.dtype,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            input_device_index=self.device_index)

    @staticmethod
    def list_devices():
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            print(p.get_device_info_by_index(i))

    list_devices = staticmethod(list_devices)
