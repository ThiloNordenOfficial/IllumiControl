import asyncio
import logging
import time
from abc import abstractmethod
from asyncio import timeout
from typing import final

from shared.TimingReceiver import TimingReceiver
from shared.shared_memory.NumpyArraySender import NumpyArraySender


class Generator(TimingReceiver):
    def __init__(self, inbound_data_senders: dict[str, NumpyArraySender], height: int, width: int, depth: int):
        super().__init__(inbound_data_senders)
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

    @abstractmethod
    def get_outbound_data_senders(self) -> dict[str, NumpyArraySender]:
        pass

    get_data_senders = abstractmethod(get_outbound_data_senders)

    @final
    def run(self):
        asyncio.run(self._generate())

    @final
    async def _generate(self):
        while not self.kill_event.is_set():
            try:
                timout_in_sec = float(self.timing_receiver.read_on_update()[0]) - time.time()
                async with timeout(timout_in_sec):
                    self.generate()
            except asyncio.TimeoutError:
                logging.warning(F"Dropped {self.__class__.__name__} step due to not finishing in time for next frame")
        self.delete()

    @abstractmethod
    def generate(self):
        pass

    run = abstractmethod(run)
