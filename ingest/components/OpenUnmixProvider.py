import argparse
import logging
import math
import time
from typing import Mapping

import numpy as np
import openunmix
import pyaudio
import torch

from ingest.IngestBase import IngestBase
from shared import GracefulKiller
from shared.CommandLineArgumentAdder import CommandLineArgumentAdder
from shared.shared_memory import QueueSender, NumpyArraySender, ByteSender
from shared.shared_memory.SmSender import SmSender


class OpenUnmixProvider(IngestBase, CommandLineArgumentAdder, GracefulKiller):
    separator = openunmix.umxhq(wiener_win_len=None)

    device = None
    model = None
    list_audio_devices = None
    audio_device = None
    sample_rate = None
    chunk_size = None
    channels = None
    audio_buffer_size = None

    def __init__(self):
        if self.list_audio_devices is not None:
            OpenUnmixProvider.list_devices()
            print("Audio devices listed, now exiting")
            exit(0)
        super().__init__()

        self.p = pyaudio.PyAudio()
        self.device_index: int = OpenUnmixProvider.audio_device \
            if OpenUnmixProvider.audio_device is not None else self.p.get_default_input_device_info()['index']
        type(self).sample_rate: int = OpenUnmixProvider.sample_rate \
            if OpenUnmixProvider.sample_rate is not None else self.detect_sample_rate()
        type(self).chunk_size: int = OpenUnmixProvider.chunk_size \
            if OpenUnmixProvider.chunk_size is not None else 4096
        type(self).channels: int = OpenUnmixProvider.channels

        logging.info(self.p.get_device_info_by_index(self.device_index))
        self.separator.to(self.device)

        self.stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            output=False,
            output_device_index=self.device_index,
            frames_per_buffer=self.chunk_size,
            input_device_index=self.device_index,
            stream_callback=self.analyse_audio,
        )
        self.stem_names = self.separator.target_models.keys()

        self.data_senders: dict[str, SmSender] = {
            f"separated_audio_{name}": ByteSender(size=4 * 8192,
                                                  shm_name=f"separated_audio_{name}", dtype=np.float32)
            for name in self.stem_names
        }

    def delete(self):
        logging.info("OpenUnmixProvider.delete: Closing audio stream and senders")
        self.stream.stop_stream()
        self.stream.close()
        for name, sender in self.data_senders:
            sender.close()

    def run(self):
        self.stream.start_stream()

    def analyse_audio(self, in_data: bytes | None, frame_count: int, time_info: Mapping[str, float],
                      status: int) -> \
            tuple[bytes | None, int] | None:
        np_audio = np.frombuffer(in_data, dtype=np.float32)
        tensor_audio = torch.tensor(np_audio, dtype=torch.float32)
        umx_audio = openunmix.utils.preprocess(tensor_audio, self.sample_rate, self.sample_rate)
        audio = umx_audio.to(self.device)

        stems = self.separator(audio)

        for i, name in enumerate(self.stem_names):
            source = stems[0, i, 0].detach().cpu().numpy()
            self.data_senders[f"separated_audio_{name}"].update(source.tobytes())
        return None, pyaudio.paAbort if self.kill_event.is_set() else pyaudio.paContinue

    def detect_sample_rate(self) -> int:
        sample_rate = self.p.get_device_info_by_index(self.device_index)['defaultSampleRate']
        if sample_rate.is_integer():
            return int(sample_rate)
        else:
            return int(math.floor(sample_rate))

    def get_outbound_data_senders(self) -> dict[str, SmSender]:
        return self.data_senders

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
        parser.add_argument("--computation-device", dest='device', type=str, default='cuda',
                            help="On what device the OpenUnmix model is run. Default is 'cuda' if available, otherwise 'cpu'.")
        parser.add_argument("--model", dest='model', type=str, default='umxhq'),
        parser.add_argument("--audio-device", dest='audio_device', type=int,
                            help="Device index of the audio input device")
        parser.add_argument("--sample-rate", dest='sample_rate', type=int,
                            help="Desired sample rate of the audio input device, if not provided the default sample rate of the device will be used")
        parser.add_argument("--chunk-size", dest='chunk_size', type=int, help="Frames per buffer")
        parser.add_argument("--channels", dest='channels', type=int, default=1,
                            help="Number of channels of the audio stream, if not provided the stream will be mono")

    @classmethod
    def apply_command_line_arguments(cls, args: argparse.Namespace):
        cls.list_audio_devices = args.list_audio_devices
        cls.audio_device = args.audio_device
        cls.sample_rate = args.sample_rate
        cls.chunk_size = args.chunk_size
        cls.channels = args.channels
        cls.device = args.device
        cls.model = args.model
