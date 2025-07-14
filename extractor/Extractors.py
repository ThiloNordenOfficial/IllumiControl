import argparse
import logging
from multiprocessing import Process

from ipcqueue.posixmq import Queue

from shared.CommandLineArgumentAdder import CommandLineArgumentAdder
from extractor.ExtractorBase import ExtractorBase
from sender.ArtNetSender import ArtNetSender
from shared.fixture import FixtureConfigurationLoader
from shared import is_valid_file
from shared.fixture.FixtureConsumer import FixtureConsumer
from shared.shared_memory.NumpyArraySender import NumpyArraySender
from shared.shared_memory.SmSender import SmSender
from shared.validators.is_valid_ip import is_valid_ip


class Extractors(FixtureConsumer):
    def __init__(self, data_senders: dict[str, SmSender]):
        logging.info("Initializing feature extractor")
        FixtureConsumer.__init__(self)
        self.dmx_queue = Queue("/dmx_queue")
        self.extractors = self._instantiate_extractors(data_senders)

    def _instantiate_extractors(self, data_senders) -> list[ExtractorBase]:
        extractors = []
        for extractor_class in ExtractorBase.__subclasses__():
            extractors.append(extractor_class(data_senders, self.fixtures))
        return extractors

    def run(self):
        logging.debug("Starting feature extractor run loop")
        extractor_processes = []
        for extractor in self.extractors:
            extractor_processes.append(Process(target=extractor.run))

        for process in extractor_processes:
            process.start()

        for process in extractor_processes:
            process.join()
