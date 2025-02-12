import argparse

from CommandLineArgumentAdder import CommandLineArgumentAdder
from shared import LoggingConfigurator


class ImageGenerator(CommandLineArgumentAdder):
    def __init__(self, args: argparse.Namespace):
        pass

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        pass

    add_command_line_arguments = staticmethod(add_command_line_arguments)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Image Generator',
        description='')

    ImageGenerator.add_command_line_arguments(parser)
    LoggingConfigurator.add_command_line_arguments(parser)

    args = parser.parse_args()

    LoggingConfigurator(args)
    ImageGenerator(args)
