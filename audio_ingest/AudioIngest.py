import argparse
import logging

import numpy as np
import opensmile
from opensmile import FeatureLevel

from audio_ingest.AudioProvider import AudioProvider
from CommandLineArgumentAdder import CommandLineArgumentAdder
from shared import LoggingConfigurator, is_valid_file
from shared.shared_memory.NumpyArraySender import NumpyArraySender


class AudioIngest(CommandLineArgumentAdder):
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
        logging.debug("Audio ingest initialized")

    def digest(self) -> np.ndarray:
        return self.smile.process_signal(
            np.frombuffer(
                # TODO WHHHHHYYY IS IT NOT LOCKING?!?!?!??!?!?!?!
                self.audio_provider.stream.read(self.audio_provider.chunk_size),
                dtype=np.int16
            ),
            self.audio_provider.sample_rate
        ).to_numpy()

    def run(self):
        logging.debug("Starting audio ingest run loop")
        while True:
            self.audio_data_sender.update(self.digest())
            logging.debug("Updated audio data")

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        parser.add_argument("--list-audio-devices", dest='list_audio_devices',
                            help="List all available audio devices and exit")
        parser.add_argument("--audio-device", dest='audio_device', required=True, type=int,
                            help="Device index of the audio input device")
        parser.add_argument("--sample-rate", dest='sample_rate', type=int,
                            help="Desired sample rate of the audio input device, if not provided the default sample rate of the device will be used")
        parser.add_argument("--chunk-size", dest='chunk_size', type=int, help="Frames per buffer")
        parser.add_argument("--channels", dest='channels', type=int,
                            help="Number of channels of the audio stream, if not provided the stream will be mono")
        parser.add_argument("--feature-set", dest='feature_set', type=lambda x: is_valid_file(parser, x), required=True)

    add_command_line_arguments = staticmethod(add_command_line_arguments)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Audio Ingest',
        description='')

    AudioIngest.add_command_line_arguments(parser)
    LoggingConfigurator.add_command_line_arguments(parser)

    args = parser.parse_args()

    LoggingConfigurator(args)
    audio_ingest = AudioIngest(args)
    logging.debug(
        F"Parameters: {audio_ingest.audio_data_sender}")
    audio_ingest.run()
