from postprocessor.PostProcessorBase import PostProcessorBase
from shared.fixture.DmxSignal import DmxSignal
from shared.fixture.FixtureSignal import FixtureSignal


class PassThroughProcessor(PostProcessorBase):
    def run_after_processing(self, fixture_signals: list[FixtureSignal], dmx_signals: list[DmxSignal]) -> list[
        DmxSignal]:
        for fixture_signal in fixture_signals:
            dmx_signals.append(DmxSignal(fixture_signal.fixture.dmx_universe, fixture_signal.channel_values))
        return dmx_signals
