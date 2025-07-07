import logging
import threading
from ingest.IngestBase import IngestBase
from shared import DataSender
from shared.shared_memory.Sender import Sender


class Ingests(DataSender):
    def __init__(self):
        logging.info("Initializing ingest")
        self.ingestors = self._instantiate_ingestors()
        self.data_senders: dict[str, Sender] = self._get_all_data_senders()

    def _instantiate_ingestors(self):
        ingestors = []
        for ingestor_class in IngestBase.__subclasses__():
            ingestors.append(ingestor_class())
        return ingestors

    def _get_all_data_senders(self) -> dict[str, Sender]:
        combined_senders = {}
        for ingestor in self.ingestors:
            combined_senders.update(ingestor.get_outbound_data_senders())
        return combined_senders

    def run(self):
        logging.debug("Starting ingest run loop")
        ingest_threads = []
        for ingestor in self.ingestors:
            ingest_threads.append(threading.Thread(target=ingestor.run))

        for ingestor in ingest_threads:
            ingestor.start()

        for ingestor in ingest_threads:
            ingestor.join()

    def get_outbound_data_senders(self) -> dict[str, Sender]:
        return self.data_senders
