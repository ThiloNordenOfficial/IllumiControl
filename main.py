import argparse
import logging
import signal
import threading

from analyser.Analysers import Analysers
from postprocessor.PostProcessors import PostProcessors
from sender.Senders import Senders
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
        self.post_processors = None
        self.senders = None
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

        self.analysers = Analysers(self.data_senders)
        self.data_senders.update(self.analysers.get_outbound_data_senders())

        self.generators = Generators(self.data_senders)
        self.data_senders.update(self.generators.get_outbound_data_senders())

        self.extractors = Extractors(self.data_senders)
        self.data_senders.update(self.extractors.get_outbound_data_senders())

        self.post_processors = PostProcessors(self.data_senders)
        self.data_senders.update(self.post_processors.get_outbound_data_senders())

        self.senders = Senders(self.data_senders)

    def start_threads(self):
        ingest_runner = threading.Thread(target=self.ingestors.run)
        analyser_runner = threading.Thread(target=self.analysers.run)
        generator_runner = threading.Thread(target=self.generators.run)
        extractor_runner = threading.Thread(target=self.extractors.run)
        post_processor_runner = threading.Thread(target=self.post_processors.run)
        sender_runner = threading.Thread(target=self.senders.run)

        self.threads = [ingest_runner, analyser_runner, generator_runner, extractor_runner,
                        post_processor_runner,
                        sender_runner]
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
