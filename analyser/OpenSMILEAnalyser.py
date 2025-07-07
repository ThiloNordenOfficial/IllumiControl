import argparse
import logging
from asyncio import timeout

import numpy as np
import opensmile
from opensmile import FeatureLevel

from analyser.AnalyserBase import AnalyserBase
from ingest import AudioProvider
from shared.CommandLineArgumentAdder import CommandLineArgumentAdder
from shared.shared_memory.ByteReceiver import ByteReceiver
from shared.shared_memory.NumpyArraySender import NumpyArraySender
from shared.shared_memory.Sender import Sender
from shared.validators.is_valid_file import is_valid_file


class OpenSmileAnalyser(AnalyserBase, CommandLineArgumentAdder):
    feature_set = None

    def __init__(self, inbound_data_senders: dict[str, Sender]):
        self.timing_sender = NumpyArraySender(shape=np.shape(np.array([1.])), dtype=np.float64)
        inbound_data_senders.update([("npa-timing-data", self.timing_sender)])
        super().__init__(inbound_data_senders)
        self.smile = opensmile.Smile(
            feature_set=self.feature_set,
            feature_level=FeatureLevel.Functionals,
        )
        self.raw_audio_data_receiver = ByteReceiver(inbound_data_senders.get("b-raw-audio-data"))
        self.audio_data_sender = NumpyArraySender(shape=(1, self.smile.num_features),
                                                  dtype=np.float64)

    def run_procedure(self):
        audio_data = self.digest()
        self.audio_data_sender.update(audio_data)

    def digest(self) -> np.ndarray:
        value: bytes = self.raw_audio_data_receiver.read_all()
        if not value:
            logging.warning("No data received from raw audio data receiver")
            return np.array([])
        signal = self.smile.process_signal(
            np.frombuffer(
                value,
                dtype=int
            ), AudioProvider.sample_rate
        ).to_numpy()
        self.timing_sender.update(np.array([1]))
        return signal

    def delete(self):
        self.raw_audio_data_receiver.close()
        self.timing_sender.close()
        self.audio_data_sender.close()
        del self.smile

    def get_outbound_data_senders(self) -> dict[str, Sender]:
        return {
            "npa-timing-data": self.timing_sender,
            "npa-audio-data": self.audio_data_sender
        }

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        parser.add_argument("--feature-set", dest='feature_set', type=lambda x: is_valid_file(parser, x), required=True)

    add_command_line_arguments = staticmethod(add_command_line_arguments)

    @classmethod
    def apply_command_line_arguments(cls, args: argparse.Namespace):
        cls.feature_set = args.feature_set
