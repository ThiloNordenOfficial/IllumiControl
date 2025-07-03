import argparse
import logging

import numpy as np
import opensmile
from opensmile import FeatureLevel

from analyser.AnalyserBase import AnalyserBase
from shared.CommandLineArgumentAdder import CommandLineArgumentAdder
from shared.shared_memory.ByteReceiver import ByteReceiver
from shared.shared_memory.NumpyArraySender import NumpyArraySender
from shared.shared_memory.Sender import Sender
from shared.validators.is_valid_file import is_valid_file


class OpenSmileAnalyser(AnalyserBase, CommandLineArgumentAdder):
    feature_set = None
    sample_rate = None

    def __init__(self, inbound_data_senders: dict[str, Sender]):
        self.timing_sender = NumpyArraySender(shape=np.shape(np.array([1.])), dtype=np.float64)
        inbound_data_senders.update([("timing-data", self.timing_sender)])
        super().__init__(inbound_data_senders)
        self.smile = opensmile.Smile(
            feature_set=self.feature_set,
            feature_level=FeatureLevel.Functionals,
            multiprocessing=True
        )
        self.raw_audio_data_receiver = ByteReceiver(inbound_data_senders.get("b-raw-audio-data"))
        self.audio_data_sender = NumpyArraySender(shape=np.shape(self.digest()),
                                                  dtype=np.float64)  # , shm_name="audio-data")

    def run_procedure(self):
        audio_data = self.digest()
        self.audio_data_sender.update(audio_data)

    def digest(self) -> np.ndarray:
        value = self.raw_audio_data_receiver.read_new()
        logging.error(value)
        # if not value:
        #     logging.warning("No data received from raw audio data receiver")
        return np.array([])
        # return self.smile.process_signal(
        #     np.frombuffer(
        #         value,
        #         dtype=np.int32
        #     ),
        #     self.sample_rate
        # ).to_numpy()

    def delete(self):
        self.raw_audio_data_receiver.close()
        self.timing_sender.close()
        self.audio_data_sender.close()
        del self.smile

    def get_outbound_data_senders(self) -> dict[str, Sender]:
        return {
            "timing-data": self.timing_sender,
            "audio-data": self.audio_data_sender
        }

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        parser.add_argument("--feature-set", dest='feature_set', type=lambda x: is_valid_file(parser, x), required=True)

    add_command_line_arguments = staticmethod(add_command_line_arguments)

    @classmethod
    def apply_command_line_arguments(cls, args: argparse.Namespace):
        cls.feature_set = args.feature_set
        cls.sample_rate = args.sample_rate if hasattr(args, 'sample_rate') else 16000
