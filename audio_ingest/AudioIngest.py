import logging
from multiprocessing import Process

from audio_ingest.AudioProvider import AudioProvider
from audio_ingest.Analyser import Analyser
from shared import DataSender
from shared.shared_memory.NumpyArraySender import NumpyArraySender


class AudioIngest(DataSender):
    def __init__(self, data_senders: dict[str, NumpyArraySender]):
        logging.debug("Initializing audio ingest")
        self.audio_provider = AudioProvider()

        data_senders.update(self.audio_provider.get_outbound_data_senders())
        self.analysers = self._instantiate_analysers(data_senders)
        self.data_senders: dict[str, NumpyArraySender] = self._get_all_data_senders(data_senders)
        logging.debug("Audio ingest initialized")

    def _instantiate_analysers(self, data_senders) -> list[Analyser]:
        analysers = []
        for analyser_class in Analyser.__subclasses__():
            analysers.append(analyser_class(data_senders))
        return analysers

    def _get_all_data_senders(self, data_senders: dict[str, NumpyArraySender]) -> dict[str, NumpyArraySender]:
        combined_senders = data_senders
        for analyser in self.analysers:
            combined_senders.update(analyser.get_outbound_data_senders())
        return combined_senders

    def run(self):
        logging.debug("Starting ingest run loop")
        analyser_processes = []
        for analyser in self.analysers:
            analyser_processes.append(Process(target=analyser.run))

        for process in analyser_processes:
            process.start()

        for process in analyser_processes:
            process.join()

    def get_outbound_data_senders(self) -> dict[str, NumpyArraySender]:
        return self.data_senders
