import logging
from multiprocessing import Process

from analyse.AnalyserBase import AnalyserBase
from analyse.TimingProviderBase import TimingProviderBase
from shared import DataSender
from shared.shared_memory import SmSender


class AnalyseModule(DataSender):
    def __init__(self, data_senders: dict[str, SmSender]):
        logging.info("Initializing audio analysers")
        self.timing_provider = self._instantiate_timing_provider(data_senders)
        data_senders.update(self.timing_provider.get_outbound_data_senders())
        self.analysers = self._instantiate_analysers(data_senders)
        self.data_senders: dict[str, SmSender] = self._get_all_data_senders(data_senders)

    @staticmethod
    def _instantiate_analysers(data_senders) -> list[AnalyserBase]:
        analysers = []
        for analyser_class in AnalyserBase.__subclasses__():
            analysers.append(analyser_class(data_senders))
        return analysers

    @staticmethod
    def _instantiate_timing_provider(data_senders: dict[str, SmSender]):
        timing_providers = TimingProviderBase.__subclasses__()
        if len(timing_providers) != 1:
            raise RuntimeError("Exactly one TimingProvider must be defined")
        timing_provider = timing_providers[0](data_senders)
        return timing_provider

    def _get_all_data_senders(self, data_senders: dict[str, SmSender]) -> dict[str, SmSender]:
        combined_senders = data_senders
        for analyser in self.analysers:
            combined_senders.update(analyser.get_outbound_data_senders())
        return combined_senders

    def run(self):
        logging.debug("Starting analyser run loop")
        analyser_processes = [Process(target=self.timing_provider.run)]
        for analyser in self.analysers:
            analyser_processes.append(Process(target=analyser.run))

        for process in analyser_processes:
            process.start()
            process.join()

    def get_outbound_data_senders(self) -> dict[str, SmSender]:
        return self.data_senders
