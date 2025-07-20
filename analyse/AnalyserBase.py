from abc import abstractmethod

from shared import DataSender
from shared.runner.TimedRunner import TimedRunner
from shared.shared_memory.SmSender import SmSender


class AnalyserBase(DataSender, TimedRunner):
    def __init__(self, data_senders: dict[str, 'SmSender']):
        super().__init__()
        self.inbound_data_senders = data_senders

    @abstractmethod
    def delete(self):
        del self.inbound_data_senders

    delete = abstractmethod(delete)
