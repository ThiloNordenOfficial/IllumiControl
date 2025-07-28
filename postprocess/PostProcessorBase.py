import logging
import time
from abc import abstractmethod
from typing import final

from shared import StatisticWriter
from shared.fixture.DmxSignal import DmxSignal
from shared.fixture.FixtureSignal import FixtureSignal
from shared.runner.PostTimeRunner import PostTimeRunner
from shared.shared_memory import SmSender


def is_list_of_type(obj, typ):
    return isinstance(obj, list) and all(isinstance(item, typ) for item in obj)


class PostProcessorBase(StatisticWriter):
    def __init__(self, data_senders: dict[str, SmSender]):
        StatisticWriter.__init__(self)
        self.data_senders = data_senders

    def run_after_processing(self, *args, **kwargs):
        start_time = time.time()
        if not (isinstance(args[0], list) and all(isinstance(x, FixtureSignal) for x in args[0])):
            raise ValueError("No fixture signals provided")
        if not (isinstance(args[1], list) and all(isinstance(x, DmxSignal) for x in args[1])):
            raise ValueError("No DMX signals provided")
        fixture_signals: list[FixtureSignal] = args[0]
        dmx_signals: list[DmxSignal] = args[1]
        result = self.run_after(fixture_signals, dmx_signals)
        self.write_statistics_time(time.time()- start_time)
        return result

    @abstractmethod
    def run_after(self, fixture_signals: list[FixtureSignal], dmx_signals: list[DmxSignal]) -> list[
        DmxSignal]:
        pass

