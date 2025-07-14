from abc import abstractmethod

from shared import TimingReceiver, StatisticWriter, DataSender, DmxQueueUser, TimedRunner
from shared.shared_memory.NumpyArraySender import NumpyArraySender


class ExtractorBase(DmxQueueUser, DataSender, TimedRunner):
    def __init__(self, inbound_data_senders: dict[str, NumpyArraySender], fixtures):
        TimedRunner.__init__(self, inbound_data_senders)
        DmxQueueUser.__init__(self)
        StatisticWriter.__init__(self)
        self.inbound_data_senders = inbound_data_senders
        self.fixtures = fixtures

    @abstractmethod
    def delete(self):
        TimingReceiver.delete(self)
        DmxQueueUser.delete(self)

        del self.inbound_data_senders
        del self.fixtures

    delete = abstractmethod(delete)
