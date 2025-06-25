import argparse
import logging

import numpy as np
import opensmile
from opensmile import FeatureLevel

from shared.CommandLineArgumentAdder import CommandLineArgumentAdder
from ingest.IngestBase import IngestBase
from shared.shared_memory.NumpyArrayReceiver import NumpyArrayReceiver
from shared.shared_memory.NumpyArraySender import NumpyArraySender
from shared.validators.is_valid_file import is_valid_file


class OpenSmileAnalyser(IngestBase, CommandLineArgumentAdder):
    feature_set = None
    sample_rate = None

    def __init__(self, inbound_data_senders: dict[str, NumpyArraySender]):
        self.timing_sender = NumpyArraySender(shape=np.shape(np.array([1.])), dtype=np.float64)
        inbound_data_senders.update([("timing-data", self.timing_sender)])
        super().__init__(inbound_data_senders)
        self.smile = opensmile.Smile(
            feature_set=self.feature_set,
            feature_level=FeatureLevel.Functionals
        )
        self.raw_audio_data_receiver = NumpyArrayReceiver(inbound_data_senders.get("raw-audio-data"))
        self.audio_data_sender = NumpyArraySender(shape=self.smile.num_features, dtype=np.float64)#, shm_name="audio-data")

    def run_procedure(self):
        logging.debug("Starting audio ingest run loop")
        logging.info("run opensmile")
        audio_data = self.digest()
        logging.info("digest finished")
        self.audio_data_sender.update(audio_data)

    def digest(self) -> np.ndarray:
        return self.smile.process_signal(
            np.frombuffer(
                self.raw_audio_data_receiver.read_on_update(),
                dtype=np.int32
            ),
            self.sample_rate
        ).to_numpy()

    def delete(self):
        self.raw_audio_data_receiver.close()
        self.timing_sender.close()
        self.audio_data_sender.close()
        del self.smile

    def get_outbound_data_senders(self) -> dict[str, NumpyArraySender]:
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
