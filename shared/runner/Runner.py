import asyncio
import logging
import time
from abc import abstractmethod

from shared import StatisticWriter


class Runner(StatisticWriter):
    def run(self):
        logging.error("Running " + self.__class__.__name__)
        asyncio.run(self._run_until_shutdown())

    async def _run_until_shutdown(self):
        while not self.kill_event.is_set():
            start_time = time.time()
            await self.run_procedure()
            if self.statistics_are_active:
                self.write_statistics_time(time.time() - start_time)
        self.delete()


    @abstractmethod
    async def run_procedure(self):
        pass

    abstractmethod(run_procedure)