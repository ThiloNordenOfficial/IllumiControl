import logging
from multiprocessing import Process

from analyser.AnalyserBase import AnalyserBase
from shared import DataSender
from shared.shared_memory.Sender import Sender


class Analyser(DataSender):
    def __init__(self, data_senders: dict[str, Sender]):
        logging.debug("Initializing audio analysers")
        self.analysers = self._instantiate_analysers(data_senders)
        self.data_senders: dict[str, Sender] = self._get_all_data_senders(data_senders)
        logging.debug("Analysers initialized")

    @staticmethod
    def _instantiate_analysers(data_senders) -> list[AnalyserBase]:
        analysers = []
        for analyser_class in AnalyserBase.__subclasses__():
            analysers.append(analyser_class(data_senders))
        return analysers

    def _get_all_data_senders(self, data_senders: dict[str, Sender]) -> dict[str, Sender]:
        combined_senders = data_senders
        for analyser in self.analysers:
            combined_senders.update(analyser.get_outbound_data_senders())
        return combined_senders

    def run(self):
        logging.debug("Starting analyser run loop")
        analyser_processes = []
        for analyser in self.analysers:
            analyser_processes.append(Process(target=analyser.run))

        for process in analyser_processes:
            process.start()

        for process in analyser_processes:
            process.join()

    def get_outbound_data_senders(self) -> dict[str, Sender]:
        return self.data_senders
