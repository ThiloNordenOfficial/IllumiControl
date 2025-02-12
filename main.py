import argparse

from CommandLineArgumentAdder import CommandLineArgumentAdder
from audio_ingest import AudioIngest
from feature_extractor import FeatureExtractor
from shared import LoggingConfigurator

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='IllumiControl',
        description='')

    for argument_adder in CommandLineArgumentAdder.__subclasses__():
        argument_adder.add_command_line_arguments(parser)

    cmdl_args = parser.parse_args()

    LoggingConfigurator(cmdl_args)
    AudioIngest(cmdl_args)
    FeatureExtractor(cmdl_args)

