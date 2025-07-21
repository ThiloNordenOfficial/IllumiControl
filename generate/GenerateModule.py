import logging
from multiprocessing import Process

from generate.GeneratorBase import GeneratorBase
from shared import DataSender
from shared.shared_memory.NumpyArraySender import NumpyArraySender
from shared.shared_memory.SmSender import SmSender


class GenerateModule(DataSender):
    def __init__(self, data_senders: dict[str, NumpyArraySender]):
        logging.info("Initializing image generator")
        self.generators = self._instantiate_generators(data_senders)
        self.data_senders: dict[str, NumpyArraySender] = self._get_all_data_senders()

    def _instantiate_generators(self, data_senders) -> list[GeneratorBase]:
        generators = []
        for generator_class in GeneratorBase.__subclasses__():
            generators.append(generator_class(data_senders))
        return generators

    def _get_all_data_senders(self) -> dict[str, NumpyArraySender]:
        combined_senders = {}
        for generator in self.generators:
            combined_senders.update(generator.get_outbound_data_senders())
        return combined_senders

    def run(self):
        logging.debug("Starting generator run loop")
        generator_processes = []
        for generator in self.generators:
            generator_processes.append(Process(target=generator.run))

        for process in generator_processes:
            process.start()
            process.join()

    def get_outbound_data_senders(self) -> dict[str, SmSender]:
        return self.data_senders
