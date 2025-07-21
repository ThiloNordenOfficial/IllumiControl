import logging
from multiprocessing import Process

from extract.ExtractorBase import ExtractorBase
from shared import DataSender
from shared.fixture.FixtureConsumer import FixtureConsumer
from shared.fixture.FixtureSignal import FixtureSignal
from shared.shared_memory import QueueSender
from shared.shared_memory.SmSender import SmSender


class ExtractModule(FixtureConsumer, DataSender):
    def __init__(self, data_senders: dict[str, SmSender]):
        logging.info("Initializing feature extractor")
        FixtureConsumer.__init__(self)
        self.fixture_signal_queue_sender = QueueSender[FixtureSignal]("fixture_signal")
        self.extractors = self._instantiate_extractors(data_senders)

    def _instantiate_extractors(self, data_senders) -> list[ExtractorBase]:
        extractors = []
        for extractor_class in ExtractorBase.__subclasses__():
            extractors.append(extractor_class(data_senders, self.fixtures, self.fixture_signal_queue_sender))
        return extractors

    def run(self):
        logging.debug("Starting feature extractor run loop")
        extractor_processes = []
        for extractor in self.extractors:
            extractor_processes.append(Process(target=extractor.run))

        for process in extractor_processes:
            process.start()
            process.join()

    def get_outbound_data_senders(self) -> dict[str, SmSender]:
        return {
            "fixture_signal_queue": self.fixture_signal_queue_sender,
        }
