import argparse
import logging
import os

import numpy as np
import opensmile
from opensmile import FeatureLevel

from analyse.TimingProviderBase import TimingProviderBase
from ingest import AudioProvider
from shared.CommandLineArgumentAdder import CommandLineArgumentAdder
from shared.shared_memory.ByteReceiver import ByteReceiver
from shared.shared_memory.NumpyArraySender import NumpyArraySender
from shared.shared_memory.SmSender import SmSender


def get_feature_set(feature_set: str):
    if feature_set == "ComParE_2016":
        return opensmile.FeatureSet.ComParE_2016
    elif feature_set == "GeMAPSv01a":
        return opensmile.FeatureSet.GeMAPSv01a
    elif feature_set == "GeMAPSv01b":
        return opensmile.FeatureSet.GeMAPSv01b
    elif feature_set == "eGeMAPSv01a":
        return opensmile.FeatureSet.eGeMAPSv01a
    elif feature_set == "eGeMAPSv01b":
        return opensmile.FeatureSet.eGeMAPSv01b
    elif feature_set == "eGeMAPSv02":
        return opensmile.FeatureSet.eGeMAPSv02
    elif feature_set == "emobase":
        return opensmile.FeatureSet.emobase
    elif os.path.exists(feature_set):
        return feature_set
    else:
        raise ValueError(
            f"Invalid feature set: {feature_set}. Must be one of the predefined sets or a valid file path.")


class OpenSmileAnalyser(TimingProviderBase, CommandLineArgumentAdder):
    feature_set = None

    def __init__(self, inbound_data_senders: dict[str, SmSender]):
        self.timing_sender = NumpyArraySender(shape=np.shape(np.array([1.])), dtype=np.float64)
        inbound_data_senders.update([("timing-data", self.timing_sender)])
        super().__init__(inbound_data_senders)

        self.smile = opensmile.Smile(
            feature_set=get_feature_set(self.feature_set),
            feature_level=FeatureLevel.Functionals,
        )
        self.raw_audio_data_receiver = ByteReceiver(inbound_data_senders.get("raw-audio-data"))
        self.audio_data_sender = NumpyArraySender(shape=(1, self.smile.num_features),
                                                  dtype=np.float64)

    async def run_procedure(self):
        audio_data = self.digest()
        self.audio_data_sender.update(audio_data)

    def digest(self) -> np.ndarray:
        value = self.raw_audio_data_receiver.read_last(AudioProvider.sample_rate*4)
        signal = self.smile.process_signal(
            value.astype(np.float32),
            AudioProvider.sample_rate
        ).to_numpy()
        self.timing_sender.update(np.array([1 / self.fps]))
        return signal

    def delete(self):
        self.raw_audio_data_receiver.close()
        self.timing_sender.close()
        self.audio_data_sender.close()
        del self.smile

    def get_outbound_data_senders(self) -> dict[str, SmSender]:
        return {
            "timing-data": self.timing_sender,
            "audio-data": self.audio_data_sender
        }

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        parser.add_argument("--feature-set", dest='feature_set', required=True)

    @classmethod
    def apply_command_line_arguments(cls, args: argparse.Namespace):
        cls.feature_set = args.feature_set
