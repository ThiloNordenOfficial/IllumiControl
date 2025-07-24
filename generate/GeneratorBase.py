from abc import abstractmethod, ABC

from shared import DataSender, StatisticWriter
from shared.runner import TimedRunner
from shared.shared_memory.NumpyArraySender import NumpyArraySender


class GeneratorBase(DataSender, TimedRunner, ABC):
    def __init__(self, data_senders: dict[str, NumpyArraySender]):
        TimedRunner.__init__(self, data_senders)
        StatisticWriter.__init__(self)

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def run_procedure(self):
        pass
