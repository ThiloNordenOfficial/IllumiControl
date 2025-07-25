from postprocess.PostProcessorBase import PostProcessorBase
from shared.fixture.DmxSignal import DmxSignal
from shared.fixture.FixtureSignal import FixtureSignal


class PassThroughProcessor(PostProcessorBase):
    def run_after(self, fixture_signals: list[FixtureSignal], dmx_signals: list[DmxSignal]) -> list[
        DmxSignal]:
        universe_map = {}

        for fixture_signal in fixture_signals:
            if fixture_signal.fixture.dmx_universe not in universe_map:
                universe_map[fixture_signal.fixture.dmx_universe] = []
                universe_map[fixture_signal.fixture.dmx_universe].extend(fixture_signal.channel_values)
            else:
                existing_channels = {cv.channel: cv for cv in universe_map[fixture_signal.fixture.dmx_universe]}
                for channel_value in fixture_signal.channel_values:
                    if channel_value.channel not in existing_channels:
                        universe_map[fixture_signal.fixture.dmx_universe].append(channel_value)

        for universe, channel_values in universe_map.items():
            if channel_values:
                dmx_signals.append(DmxSignal(universe, channel_values))

        return dmx_signals
