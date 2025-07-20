import asyncio
import time
from abc import abstractmethod

from shared import TimingReceiver, StatisticWriter
from shared.fixture.DmxSignal import DmxSignal
from shared.fixture.FixtureSignal import FixtureSignal
from shared.runner.Runner import Runner
from shared.shared_memory import SmSender


class PostProcessorRunner(StatisticWriter, TimingReceiver):
    def __init__(self, inbound_data_senders: dict[str, 'SmSender']):
        TimingReceiver.__init__(self, inbound_data_senders)
        StatisticWriter.__init__(self)

    def run(self, fixture_signals: list[FixtureSignal], dmx_signals: list[DmxSignal]) -> list[
        DmxSignal]:
        start_time = time.time()
        dmx_signals = self.run_after_processing(fixture_signals, dmx_signals)
        if self.statistics_are_active:
            self.write_statistics(time.time() - start_time)
        return dmx_signals

    @abstractmethod
    def run_after_processing(self, fixture_signals: list[FixtureSignal], dmx_signals: list[DmxSignal]) -> list[
        DmxSignal]:
        pass

    abstractmethod(run_after_processing)
