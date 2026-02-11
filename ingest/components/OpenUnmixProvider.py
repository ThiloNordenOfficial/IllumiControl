import argparse
from typing import Mapping

import pyaudio
import torch

from ingest.IngestBase import IngestBase
from shared import GracefulKiller
from shared.CommandLineArgumentAdder import CommandLineArgumentAdder
from shared.shared_memory.SmSender import SmSender


class OpenUnmixProvider(IngestBase, CommandLineArgumentAdder, GracefulKiller):
    device = None
    model = None

    def __init__(self):
        super().__init__()
        self.separator = (torch.hub.load('sigsep/open-unmix-pytorch', self.model)
                          .to(self.device))
        self.stem_names = self.separator.target_models
        self.data_sender = {}

    def delete(self):
        pass

    def run(self):
        pass

    def analyse_audio_and_write_to_memory(self, in_data: bytes | None, frame_count: int, time_info: Mapping[str, float],
                                          status: int) -> \
            tuple[bytes | None, int] | None:
        stems = self.separator(in_data)
        for i, name in self.stem_names:
            source = stems[0, i].cpu()
            self.data_sender[name].update(source)
        return None, pyaudio.paAbort if self.kill_event.is_set() else pyaudio.paContinue

    def get_outbound_data_senders(self) -> dict[str, SmSender]:
        return self.data_sender

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        parser.add_argument("--computation-device", dest='device', type=str, default='cuda',
                            help="On what device the OpenUnmix model is run. Default is 'cuda' if available, otherwise 'cpu'.")
        parser.add_argument("--model", dest='model', type=str, default='umxhq')

    @classmethod
    def apply_command_line_arguments(cls, args: argparse.Namespace):
        cls.device = args.device
        cls.model = args.model
