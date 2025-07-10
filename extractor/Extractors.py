import argparse
import logging
from multiprocessing import Process

from ipcqueue.posixmq import Queue

from shared.CommandLineArgumentAdder import CommandLineArgumentAdder
from extractor.ExtractorBase import ExtractorBase
from sender.DmxSender import DmxSender
from shared.fixture import FixtureConfigurationLoader
from shared import is_valid_file
from shared.shared_memory.NumpyArraySender import NumpyArraySender
from shared.validators.is_valid_ip import is_valid_ip


class Extractors(CommandLineArgumentAdder):
    fixture_config = None
    artnet_ip = None

    def __init__(self, data_senders: dict[str, NumpyArraySender]):
        logging.info("Initializing feature extractor")
        self.fixtures = FixtureConfigurationLoader(self.fixture_config).fixtures
        self.dmx_queue = Queue("/dmx_queue")
        self.dmx_sender = DmxSender(data_senders, self.artnet_ip, fixtures=self.fixtures)
        self.extractors = self._instantiate_extractors(data_senders)

    def _instantiate_extractors(self, data_senders) -> list[ExtractorBase]:
        extractors = []
        for extractor_class in ExtractorBase.__subclasses__():
            extractors.append(extractor_class(data_senders, self.fixtures))
        return extractors

    def run(self):
        logging.debug("Starting feature extractor run loop")
        extractor_processes = []
        sender_process = Process(target=self.dmx_sender.run)
        for extractor in self.extractors:
            extractor_processes.append(Process(target=extractor.run))

        for process in extractor_processes:
            process.start()
        sender_process.start()

        for process in extractor_processes:
            process.join()
        sender_process.join()

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        parser.add_argument("-fc", "--fixture-config", dest='fixture_config', required=True,
                            type=lambda x: is_valid_file(parser, x), help="Path to the fixture configuration file")
        parser.add_argument("--artnet-ip", dest='artnet_ip', required=True, type=lambda x: is_valid_ip(parser, x),
                            help="IP of the artnet server")

    add_command_line_arguments = staticmethod(add_command_line_arguments)

    @classmethod
    def apply_command_line_arguments(cls, args: argparse.Namespace):
        cls.artnet_ip = args.artnet_ip
        cls.fixture_config = args.fixture_config