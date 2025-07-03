import argparse
import logging
import signal
import threading

from analyser.Analyser import Analyser
from shared.CommandLineArgumentAdder import CommandLineArgumentAdder
from ingest import Ingests
from extractor import Extractors
from generator import Generators
from shared import ConfigReader, GracefulKiller, LoggingConfigurator


class IllumiControl:
    def __init__(self):
        self.data_senders = {}
        self.ingestors = None
        self.analysers = None
        self.generators = None
        self.extractors = None
        self.threads = []

    def prepare_commandline_arguments(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            prog='IllumiControl',
            description='')
        ConfigReader.add_command_line_arguments(parser)
        config_arg = parser.parse_args()

        for argument_adder in CommandLineArgumentAdder.__subclasses__():
            argument_adder.add_command_line_arguments(parser)
        ConfigReader(config_arg, parser)

        return parser.parse_args()

    def apply_commandline_arguments(self, args: argparse.Namespace):
        for argument_adder in CommandLineArgumentAdder.__subclasses__():
            argument_adder.apply_command_line_arguments(args)

    def prepare_and_apply_commandline_arguments(self):
        cmdl_args = self.prepare_commandline_arguments()
        self.apply_commandline_arguments(cmdl_args)

    @staticmethod
    def set_shutdown_event(signum, frame):
        GracefulKiller.kill_event.set()
        logging.warning("Starting shutting down IllumiControl")

    @staticmethod
    def setup_graceful_shutdown():
        signal.signal(signal.SIGINT, IllumiControl.set_shutdown_event)
        signal.signal(signal.SIGTERM, IllumiControl.set_shutdown_event)

    def initialize_components(self):
        self.ingestors = Ingests()
        self.data_senders.update(self.ingestors.get_outbound_data_senders())

        self.analysers = Analyser(self.data_senders)
        self.data_senders.update(self.analysers.get_outbound_data_senders())

        logging.error(self.data_senders)
        self.generators = Generators(self.data_senders)
        self.data_senders.update(self.generators.get_outbound_data_senders())

        self.extractors = Extractors(self.data_senders)
        # If postprocessing is done via shared memory, comment this in
        # self.data_senders.update(self.feature_extractor.get_outbound_data_senders())

    def start_threads(self):
        ingest_runner = threading.Thread(target=self.ingestors.run)
        analyser_runner = threading.Thread(target=self.analysers.run)
        generator_runner = threading.Thread(target=self.generators.run)
        extractor_runner = threading.Thread(target=self.extractors.run)

        self.threads = [ingest_runner, analyser_runner, generator_runner, extractor_runner]
        for thread in self.threads:
            thread.start()

    def join_threads(self):
        for thread in self.threads:
            thread.join()

    def run(self):
        self.setup_graceful_shutdown()
        self.prepare_and_apply_commandline_arguments()

        LoggingConfigurator()

        self.initialize_components()
        self.start_threads()

        self.join_threads()

        logging.warning("Graceful shutdown of IllumiControl completed")


if __name__ == "__main__":
    IllumiControl().run()
