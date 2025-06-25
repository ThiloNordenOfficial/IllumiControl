import argparse
import logging
import math
from typing import Mapping

import numpy as np
import pyaudio

from shared.CommandLineArgumentAdder import CommandLineArgumentAdder
from shared import GracefulKiller, DataSender
from shared.shared_memory.NumpyArraySender import NumpyArraySender


class AudioProvider(CommandLineArgumentAdder, GracefulKiller, DataSender):
    list_audio_devices = None
    audio_device = None
    sample_rate = None
    chunk_size = None
    channels = None

    def __init__(self):
        if self.list_audio_devices is not None:
            AudioProvider.list_devices()
            print("Audio devices listed, now exiting")
            exit(0)

        self.p = pyaudio.PyAudio()
        self.device_index: int = AudioProvider.audio_device \
            if AudioProvider.audio_device is not None else self.p.get_default_input_device_info()['index']
        self.sample_rate: int = AudioProvider.sample_rate \
            if AudioProvider.sample_rate is not None else self.detect_sample_rate()
        self.chunk_size: int = AudioProvider.chunk_size \
            if AudioProvider.chunk_size is not None else self.detect_chunk_size()
        self.channels: int = AudioProvider.channels if AudioProvider.channels is not None else 1
        self.dtype = pyaudio.paInt32
        self.stream: pyaudio.Stream = self.setup_stream()
        self.time_between_chunks: float = self.sample_rate / self.chunk_size
        # TODO SHAPE should be determined by chunk size and channels in ring buffer
        self.raw_audio_data_sender = NumpyArraySender(shape=np.shape((3, 3)),
                                                      dtype=np.int32)  # shm_name="raw-audio-dataasdf")

    def delete(self):
        self.stream.close()
        self.raw_audio_data_sender.close()

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
            input_device_index=self.device_index,
            stream_callback=self.write_audio_to_memory
        )

    def get_next_bytes_of_stream(self):
        return self.stream.read(self.chunk_size)

    @staticmethod
    def write_audio_to_memory(in_data: bytes | None, frame_count: int, time_info: Mapping[str, float], status: int) -> \
            tuple[bytes | None, int] | None:
        logging.error(frame_count)
        return in_data, frame_count

    def get_outbound_data_senders(self) -> dict[str, NumpyArraySender]:
        return {
            "raw-audio-data": self.raw_audio_data_sender,
        }

    @staticmethod
    def list_devices():
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            print(p.get_device_info_by_index(i))

    list_devices = staticmethod(list_devices)

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        parser.add_argument("--list-audio-devices", dest='list_audio_devices',
                            help="List all available audio devices and exit")
        parser.add_argument("--audio-device", dest='audio_device', type=int,
                            help="Device index of the audio input device")
        parser.add_argument("--sample-rate", dest='sample_rate', type=int,
                            help="Desired sample rate of the audio input device, if not provided the default sample rate of the device will be used")
        parser.add_argument("--chunk-size", dest='chunk_size', type=int, help="Frames per buffer")
        parser.add_argument("--channels", dest='channels', type=int,
                            help="Number of channels of the audio stream, if not provided the stream will be mono")

    @classmethod
    def apply_command_line_arguments(cls, args: argparse.Namespace):
        cls.list_audio_devices = args.list_audio_devices
        cls.audio_device = args.audio_device
        cls.sample_rate = args.sample_rate
        cls.chunk_size = args.chunk_size
        cls.channels = args.channels
