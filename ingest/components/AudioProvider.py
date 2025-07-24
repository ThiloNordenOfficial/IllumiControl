import argparse
import logging
import math
from typing import Mapping

import pyaudio

from ingest.IngestBase import IngestBase
from shared import GracefulKiller
from shared.CommandLineArgumentAdder import CommandLineArgumentAdder
from shared.shared_memory.ByteSender import ByteSender
from shared.shared_memory.SmSender import SmSender


class AudioProvider(IngestBase, CommandLineArgumentAdder, GracefulKiller):
    list_audio_devices = None
    audio_device = None
    sample_rate = None
    chunk_size = None
    channels = None
    audio_buffer_size = None

    def __init__(self):
        if self.list_audio_devices is not None:
            AudioProvider.list_devices()
            print("Audio devices listed, now exiting")
            exit(0)
        super().__init__()

        self.p = pyaudio.PyAudio()
        self.device_index: int = AudioProvider.audio_device \
            if AudioProvider.audio_device is not None else self.p.get_default_input_device_info()['index']
        type(self).sample_rate: int = AudioProvider.sample_rate \
            if AudioProvider.sample_rate is not None else self.detect_sample_rate()
        type(self).chunk_size: int = AudioProvider.chunk_size \
            if AudioProvider.chunk_size is not None else self.detect_chunk_size()
        type(self).channels: int = AudioProvider.channels
        type(self).audio_buffer_size = AudioProvider.audio_buffer_size \
            if AudioProvider.audio_buffer_size is not None else self.sample_rate * 30  # Default to 30 seconds of audio buffer
        self.dtype = pyaudio.paInt32
        self.raw_audio_data_sender = ByteSender(self.audio_buffer_size)
        self.stream = self.p.open(
            format=self.dtype,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            output=False,
            frames_per_buffer=self.chunk_size,
            input_device_index=self.device_index,
            stream_callback=self.write_audio_to_memory,
        )

    def delete(self):
        logging.info("AudioProvider.delete: Closing audio stream and sender")
        self.stream.stop_stream()
        self.stream.close()
        self.raw_audio_data_sender.close()

    def detect_sample_rate(self) -> int:
        sample_rate = self.p.get_device_info_by_index(self.device_index)['defaultSampleRate']
        if sample_rate.is_integer():
            return int(sample_rate)
        else:
            return int(math.floor(sample_rate))

    def detect_chunk_size(self) -> int:
        return int(math.floor(self.sample_rate * (1 / 6)))

    def run(self):
        self.stream.start_stream()

    def write_audio_to_memory(self, in_data: bytes | None, frame_count: int, time_info: Mapping[str, float],
                              status: int) -> \
            tuple[bytes | None, int] | None:
        self.raw_audio_data_sender.update(in_data)
        return None, pyaudio.paAbort if self.kill_event.is_set() else pyaudio.paContinue

    def get_outbound_data_senders(self) -> dict[str, SmSender]:
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
        parser.add_argument("--channels", dest='channels', type=int, default=1,
                            help="Number of channels of the audio stream, if not provided the stream will be mono")
        parser.add_argument("--audio-buffer-size", dest='audio_buffer_size', type=int)

    @classmethod
    def apply_command_line_arguments(cls, args: argparse.Namespace):
        cls.list_audio_devices = args.list_audio_devices
        cls.audio_device = args.audio_device
        cls.sample_rate = args.sample_rate
        cls.chunk_size = args.chunk_size
        cls.channels = args.channels
        cls.audio_buffer_size = args.audio_buffer_size
