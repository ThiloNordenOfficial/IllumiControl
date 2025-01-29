import json
from Fixture import Fixture
import win32api
import win32process


class FixtureConfigurationLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.configuration = None

    def load_configuration(self):
        with open(self.file_path, 'r') as file:
            self.configuration = json.load(file)

    def get_configuration(self):
        return self.configuration


def main(path: str) -> [Fixture]:
    loader = FixtureConfigurationLoader(path)
    loader.load_configuration()
    config = loader.get_configuration()
    fixtures = []
    config_universes = config['universes']
    for config_universe in config_universes:
        for config_fixture in config_universe['fixtures']:
            fixture_addresses = []
            for address in config_fixture['dmx_addresses']:
                fixture_addresses.append((address['channel'], address['channel_type']))
            fixtures.append(Fixture(config_fixture['id'], config_fixture['type'], config_universe['id'],
                                    fixture_addresses, tuple[int, int, int]((config_fixture['position']))))
    return fixtures


if __name__ == "__main__":
    print(main("fixture_config.json"))
