from abc import abstractmethod

from shared import DataSender
from shared.runner.TimedRunner import TimedRunner
from shared.shared_memory.SmSender import SmSender


class AnalyserBase(DataSender, TimedRunner):
    def __init__(self, data_senders: dict[str, 'SmSender']):
        DataSender.__init__(self)
        TimedRunner.__init__(self, data_senders)

    @abstractmethod
    def get_outbound_data_senders(self) -> dict[str, SmSender]:
        pass

    @abstractmethod
    async def run_procedure(self):
        pass
