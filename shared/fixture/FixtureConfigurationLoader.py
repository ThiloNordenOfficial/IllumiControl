import json
import logging

from shared.fixture.Fixture import Fixture


class FixtureConfigurationLoader:
    _instance = None

    def __new__(cls, file_path):
        if cls._instance is None:
            cls._instance = super(FixtureConfigurationLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self, file_path):
        if not hasattr(self, 'initialized'):
            self.file_path = file_path
            self.configuration = None
            self.load_configuration()
            self.fixtures = self.load_fixtures_from_configuration()
            self.initialized = True

    def load_configuration(self):
        logging.debug(f"Loading configuration from {self.file_path}")
        with open(self.file_path, 'r') as file:
            self.configuration = json.load(file)

    def load_fixtures_from_configuration(self) -> list[Fixture]:
        config = self.configuration
        fixtures = []
        config_universes = config['universes']
        for config_universe in config_universes:
            for config_fixture in config_universe['fixtures']:
                fixture_addresses = []
                for address in config_fixture['dmx_addresses']:
                    fixture_addresses.append((address['channel'], address['channel_type']))
                fixtures.append(
                    Fixture(config_fixture['id'], config_fixture['type'], config_universe['id'],
                            fixture_addresses, tuple[int, int, int]((config_fixture['position'])))
                )
        logging.debug(f"Loaded {len(fixtures)} fixtures")
        return fixtures
