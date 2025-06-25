import asyncio
import logging
import time
from abc import abstractmethod
from asyncio import timeout
from typing import final

from shared import StatisticWriter
from shared.Runner import Runner
from shared.shared_memory.NumpyArrayReceiver import NumpyArrayReceiver
from shared.shared_memory.NumpyArraySender import NumpyArraySender


class TimedRunner(Runner):

    def __init__(self, inbound_data_senders: dict[str, NumpyArraySender]):
        super().__init__()
        self.timing_receiver = NumpyArrayReceiver(inbound_data_senders.get("timing-data"))

    def delete(self):
        super().delete()
        self.timing_receiver.close()

    @abstractmethod
    def run_procedure(self):
        pass

    abstractmethod(run_procedure)

    @final
    def run(self):
        asyncio.run(self._run_until_shutdown())

    @final
    async def _run_until_shutdown(self):
        while not self.kill_event.is_set():
            start_time = time.time()
            try:
                timout_in_sec = float(self.timing_receiver.read_on_update()[0]) - start_time
                async with timeout(timout_in_sec):
                    self.run_procedure()
            except asyncio.TimeoutError:
                logging.warning(F"Dropped {self.__class__.__name__} step due to not finishing in time for next frame")
            if self.statistics_are_active:
                self.write_statistics(time.time() - start_time)
        self.delete()
