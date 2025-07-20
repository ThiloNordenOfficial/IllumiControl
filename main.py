import argparse
import logging
import signal
from multiprocessing import Process
from shared.CommandLineArgumentAdder import CommandLineArgumentAdder
from shared import ConfigReader, GracefulKiller, LoggingConfigurator

from ingest import IngestModule
from analyse import AnalyseModule
from generate import GenerateModule
from extract import ExtractModule
from postprocess import PostProcessModule
from send import SendModule


class IllumiControl:
    def __init__(self):
        self.data_senders = {}
        self.ingest = None
        self.analyse = None
        self.generate = None
        self.extract = None
        self.post_process = None
        self.send = None
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
        self.ingest = IngestModule()
        self.data_senders.update(self.ingest.get_outbound_data_senders())

        self.analyse = AnalyseModule(self.data_senders)
        self.data_senders.update(self.analyse.get_outbound_data_senders())

        self.generate = GenerateModule(self.data_senders)
        self.data_senders.update(self.generate.get_outbound_data_senders())

        self.extract = ExtractModule(self.data_senders)
        self.data_senders.update(self.extract.get_outbound_data_senders())

        self.post_process = PostProcessModule(self.data_senders)
        self.data_senders.update(self.post_process.get_outbound_data_senders())

        self.send = SendModule(self.data_senders)

    def start_threads(self):
        ingest_runner = Process(target=self.ingest.run, name='Ingest')
        analyser_runner = Process(target=self.analyse.run, name='Analyse')
        generator_runner = Process(target=self.generate.run, name='Generate')
        extractor_runner = Process(target=self.extract.run, name='Extract')
        post_processor_runner = Process(target=self.post_process.run, name='PostProcess')
        sender_runner = Process(target=self.send.run, name='Send')

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
