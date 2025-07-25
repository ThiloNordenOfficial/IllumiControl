import logging
from abc import abstractmethod

from shared.fixture import FixtureConsumer
from shared.runner.TimedRunner import TimedRunner
from shared.shared_memory import SmSender, QueueSender


class ExtractorBase(TimedRunner, FixtureConsumer):
    def __init__(self, data_senders: dict[str, SmSender]):
        TimedRunner.__init__(self, data_senders)
        FixtureConsumer.__init__(self)
        logging.error(SmSender.as_type(data_senders.get("fixture_signal_queue"), QueueSender).name)
        self.fixture_signal_queue_sender = QueueSender(
            SmSender.as_type(data_senders.get("fixture_signal_queue"), QueueSender).name)

    @abstractmethod
    async def run_procedure(self):
        pass
