from abc import abstractmethod

from shared import DataSender, StatisticWriter
from shared.runner import TimedRunner
from shared.shared_memory.NumpyArraySender import NumpyArraySender


class GeneratorBase(DataSender, TimedRunner):
    def __init__(self, data_senders: dict[str, NumpyArraySender]):
        TimedRunner.__init__(self, data_senders)
        StatisticWriter.__init__(self)
        self.data_senders = data_senders

    @abstractmethod
    def delete(self):
        super().delete()
        del self.data_senders

    delete = abstractmethod(delete)
