import asyncio
import logging
import time
from abc import abstractmethod
from asyncio import timeout
from typing import final

from shared import TimingReceiver, StatisticWriter
from shared.DmxQueueUser import DmxQueueUser
from shared.shared_memory.NumpyArraySender import NumpyArraySender


class Extractor(TimingReceiver, DmxQueueUser, StatisticWriter):
    def __init__(self, inbound_data_senders: dict[str, NumpyArraySender], fixtures):
        TimingReceiver.__init__(self, inbound_data_senders)
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

    @final
    def run(self):
        asyncio.run(self._extract())

    @final
    async def _extract(self):
        while not self.kill_event.is_set():
            start_time = time.time()
            try:
                timout_in_sec = float(self.timing_receiver.read_on_update()[0]) - start_time
                async with timeout(timout_in_sec):
                    self.extract()
            except asyncio.TimeoutError:
                logging.warning(F"Dropped {self.__class__.__name__} step due to not finishing in time for next frame")
            if self.statistics_are_active:
                self.write_statistics(time.time() - start_time)
        self.delete()

    @abstractmethod
    def extract(self):
        pass

    extract = abstractmethod(extract)
