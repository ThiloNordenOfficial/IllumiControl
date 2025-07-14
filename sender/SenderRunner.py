import asyncio
from abc import abstractmethod

from shared import Runner, TimingReceiver, SmSender


class SenderRunner(Runner, TimingReceiver):
    def __init__(self, inbound_data_senders: dict[str, 'SmSender']):
        Runner.__init__(self)
        TimingReceiver.__init__(self, inbound_data_senders)

    async def run_procedure(self):
        await asyncio.sleep(float(self.timing_receiver.read_on_update()[0]))
        self.run_after_processing()

    @abstractmethod
    def run_after_processing(self):
        pass

    abstractmethod(run_after_processing)
