import asyncio
import time
from abc import abstractmethod

from shared import StatisticWriter


class Runner(StatisticWriter):
    def __init__(self):
        StatisticWriter.__init__(self)
        self.start_time = time.time()

    def run(self):
        asyncio.run(self._run_until_shutdown())

    async def _run_until_shutdown(self):
        while not self.kill_event.is_set():
            self.start_time = time.time()
            await self.run_procedure()
            self.write_statistics_time(time.time() - self.start_time)
        self.delete()

    @abstractmethod
    async def run_procedure(self):
        pass

    abstractmethod(run_procedure)
