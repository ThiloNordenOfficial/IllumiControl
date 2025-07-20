from abc import abstractmethod

from shared import TimedRunner, StatisticWriter
from shared.DataSender import DataSender
from shared.shared_memory.NumpyArraySender import NumpyArraySender


class GeneratorBase(DataSender, TimedRunner):
    def __init__(self, inbound_data_senders: dict[str, NumpyArraySender], height: int, width: int, depth: int):
        TimedRunner.__init__(self, inbound_data_senders)
        StatisticWriter.__init__(self)
        self.inbound_data_senders = inbound_data_senders
        self.height = height
        self.width = width
        self.depth = depth

    @abstractmethod
    def delete(self):
        super().delete()
        del self.inbound_data_senders
        del self.height
        del self.width
        del self.depth

    delete = abstractmethod(delete)
