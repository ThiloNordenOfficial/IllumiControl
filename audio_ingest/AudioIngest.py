import argparse
import logging
import time

import numpy as np
import opensmile
from opensmile import FeatureLevel

from audio_ingest.AudioProvider import AudioProvider
from CommandLineArgumentAdder import CommandLineArgumentAdder
from shared import is_valid_file, GracefulKiller
from shared.shared_memory.NumpyArraySender import NumpyArraySender


class AudioIngest(CommandLineArgumentAdder, GracefulKiller):
    def __init__(self, args: argparse.Namespace):
        logging.debug("Initializing audio ingest")

        if args.list_audio_devices is not None:
            AudioProvider.list_devices()
            print("Audio devices listed, now exiting")
            exit(0)

        self.audio_provider = AudioProvider(
            device_index=args.audio_device,
            sample_rate=args.sample_rate,
            chunk_size=args.chunk_size
        )
        self.smile = opensmile.Smile(
            feature_set=args.feature_set,
            feature_level=FeatureLevel.Functionals
        )
        self.audio_data_sender = NumpyArraySender(np.shape(self.digest()))
        self.timing_sender = NumpyArraySender(shape=np.shape(np.array([1.])), dtype=np.float64)
        logging.debug("Audio ingest initialized")

    def delete(self):
        del self.audio_provider
        del self.smile
        del self.audio_data_sender
        del self.timing_sender

    def digest(self) -> np.ndarray:
        return self.smile.process_signal(
            np.frombuffer(
                self.audio_provider.get_next_bytes_of_stream(),
                dtype=np.int32
            ),
            self.audio_provider.sample_rate
        ).to_numpy()

    def run(self):
        logging.debug("Starting audio ingest run loop")
        time_between_chunks = self.audio_provider.time_between_chunks
        while not self.kill_event.is_set():
            audio_data = self.digest()
            self.timing_sender.update(np.array([time.time() + time_between_chunks]))
            self.audio_data_sender.update(audio_data)
        self.delete()

    def get_data_senders(self) -> dict[str, NumpyArraySender]:
        return {
            "audio-data": self.audio_data_sender,
            "timing-data": self.timing_sender
        }

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
        parser.add_argument("--feature-set", dest='feature_set', type=lambda x: is_valid_file(parser, x), required=True)

    add_command_line_arguments = staticmethod(add_command_line_arguments)
