import argparse
from abc import abstractmethod

from shared import DataSender
from shared.CommandLineArgumentAdder import CommandLineArgumentAdder
from shared.runner.Runner import Runner


class TimingProviderBase(Runner, DataSender, CommandLineArgumentAdder):
    fps = None

    def __init__(self, inbound_data_senders: dict[str, 'SmSender']):
        super().__init__()
        self.inbound_data_senders = inbound_data_senders

    @abstractmethod
    def delete(self):
        del self.inbound_data_senders

    delete = abstractmethod(delete)

    @abstractmethod
    async def run_procedure(self):
        pass

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        parser.add_argument("--fps", dest="fps", type=int, default=6,
                            help="Frames per second dictate how long all other modules have for processing the data.")

    add_command_line_arguments = staticmethod(add_command_line_arguments)

    @classmethod
    def apply_command_line_arguments(cls, args: argparse.Namespace):
        cls.fps = args.fps
