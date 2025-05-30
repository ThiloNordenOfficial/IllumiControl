import argparse
from abc import abstractmethod


class CommandLineArgumentAdder(object):

    @staticmethod
    @abstractmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        pass

    @classmethod
    @abstractmethod
    def apply_command_line_arguments(cls,  args: argparse.Namespace):
        pass
