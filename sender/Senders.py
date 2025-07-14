import logging
import threading

from sender.SenderBase import SenderBase
from shared.fixture.FixtureConsumer import FixtureConsumer
from shared.shared_memory import SmSender


class Senders(object):
    def __init__(self, data_senders: dict[str, SmSender]):
        logging.info("Initializing outbound senders")
        self.fixtures = FixtureConsumer().fixtures
        self.out_senders = self._instantiate_senders(data_senders)

    def _instantiate_senders(self, data_senders) -> list[SenderBase]:
        senders = []
        for sender_class in SenderBase.__subclasses__():
            senders.append(sender_class(data_senders))
        return senders

    def run(self):
        logging.debug("Starting sender run loop")
        sender_threads = []
        for sender in self.out_senders:
            sender_threads.append(threading.Thread(target=sender.run))

        for sender in sender_threads:
            sender.start()

        for sender in sender_threads:
            sender.join()
