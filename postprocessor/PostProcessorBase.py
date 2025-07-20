from abc import abstractmethod

from postprocessor.PostProcessorRunner import PostProcessorRunner
from shared.fixture.DmxSignal import DmxSignal
from shared.fixture.FixtureSignal import FixtureSignal


class PostProcessorBase(PostProcessorRunner):

    @abstractmethod
    def run_after_processing(self, fixture_signals: list[FixtureSignal], dmx_signals: list[DmxSignal]) -> list[
        DmxSignal]:
        pass
