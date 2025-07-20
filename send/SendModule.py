import asyncio
import logging

from send.SenderBase import SenderBase
from shared import NumpyArrayReceiver
from shared.fixture.DmxSignal import DmxSignal
from shared.fixture.FixtureConsumer import FixtureConsumer
from shared.runner.Runner import Runner
from shared.shared_memory import SmSender
from shared.shared_memory.QueueReceiver import QueueReceiver


class SendModule(Runner):

    def __init__(self, data_senders: dict[str, SmSender]):
        super().__init__()
        logging.info("Initializing outbound senders")
        self.fixtures = FixtureConsumer().fixtures
        self.senders = self._instantiate_senders(data_senders, self.fixtures)
        self.post_processing_finished_receiver = NumpyArrayReceiver(data_senders.get('post_processing_finished'))
        self.dmx_value_queue = QueueReceiver[DmxSignal](data_senders.get('dmx_queue'))

    def delete(self):
        super().delete()

    def _instantiate_senders(self, data_senders, fixtures) -> list[SenderBase]:
        senders = []
        for sender_class in SenderBase.__subclasses__():
            senders.append(sender_class(data_senders, fixtures))
        return senders


    async def run_procedure (self):
        self.post_processing_finished_receiver.read_on_update()
        dmx_values = self.dmx_value_queue.get_all_present()
        threads = []
        for sender in self.senders:
            threads.append(asyncio.to_thread(sender.send, dmx_values))
        await asyncio.gather(*threads)