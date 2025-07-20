from abc import abstractmethod

from shared import StatisticWriter
from shared.fixture.FixtureSignal import FixtureSignal
from shared.shared_memory import SmSender, QueueSender
from shared.runner.TimedRunner import TimedRunner


class ExtractorBase(TimedRunner):
    def __init__(self, inbound_data_senders: dict[str, SmSender], fixtures, fixture_signal_queue_sender: QueueSender[FixtureSignal]):
        TimedRunner.__init__(self, inbound_data_senders)
        StatisticWriter.__init__(self)
        self.fixtures = fixtures
        self.fixture_signal_queue_sender = fixture_signal_queue_sender

    @abstractmethod
    async def run_procedure(self):
        pass
