import asyncio
import logging

from ingest.IngestBase import IngestBase
from shared import DataSender
from shared.shared_memory.SmSender import SmSender


class IngestModule(DataSender):
    def __init__(self):
        logging.info("Initializing ingest")
        self.ingestors = self._instantiate_ingestors()
        self.data_senders: dict[str, SmSender] = self._get_all_data_senders()

    def _instantiate_ingestors(self):
        ingestors = []
        for ingestor_class in IngestBase.__subclasses__():
            ingestors.append(ingestor_class())
        return ingestors

    def _get_all_data_senders(self) -> dict[str, SmSender]:
        combined_senders = {}
        for ingestor in self.ingestors:
            combined_senders.update(ingestor.get_outbound_data_senders())
        return combined_senders

    def run(self):
        logging.debug("Starting ingest run loop")
        asyncio.run(self._run())

    async def _run(self):
        ingest_threads = []
        for ingestor in self.ingestors:
            ingest_threads.append(asyncio.to_thread(ingestor.run))
        await asyncio.gather(*ingest_threads)

    def get_outbound_data_senders(self) -> dict[str, SmSender]:
        return self.data_senders
