import argparse
import logging

from generate import GeneratorBase
from shared import CommandLineArgumentAdder
from shared.shared_memory import SmSender


class PerlinGenerator(GeneratorBase, CommandLineArgumentAdder):

    def __init__(self, data_senders):
        GeneratorBase.__init__(self, data_senders)
        CommandLineArgumentAdder.__init__(self)
        self.outbound_data_senders = {}

    def delete(self):
        pass

    async def run_procedure(self):
        pass

    def get_outbound_data_senders(self) -> dict[str, SmSender]:
        return self.outbound_data_senders

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        # parser.add_argument("--max-loudness", dest='max_loudness', type=float)
        pass

    add_command_line_arguments = staticmethod(add_command_line_arguments)

    @classmethod
    def apply_command_line_arguments(cls, args: argparse.Namespace):
        pass