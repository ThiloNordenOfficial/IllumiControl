from abc import abstractmethod

from sender.SenderRunner import SenderRunner
from shared import  DmxQueueUser, Runner
from shared.fixture.FixtureConsumer import FixtureConsumer
from shared.shared_memory.SmSender import SmSender


class SenderBase(DmxQueueUser, SenderRunner, FixtureConsumer):

    def __init__(self, inbound_data_senders: dict[str, SmSender]):
        DmxQueueUser.__init__(self)
        SenderRunner.__init__(self,inbound_data_senders)
        FixtureConsumer.__init__(self)

    def delete(self):
        DmxQueueUser.delete(self)
        SenderRunner.delete(self)

    @abstractmethod
    async def run_after_processing(self):
        pass
    abstractmethod(run_after_processing)

