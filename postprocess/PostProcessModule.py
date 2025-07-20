import logging

import numpy as np

from postprocess.PostProcessorBase import PostProcessorBase
from shared import DataSender, GracefulKiller
from shared.fixture.DmxSignal import DmxSignal
from shared.fixture.FixtureSignal import FixtureSignal
from shared.shared_memory import SmSender, QueueReceiver, NumpyArraySender, QueueSender


class PostProcessModule(GracefulKiller, DataSender):

    def __init__(self, data_senders: dict[str, SmSender]):
        DataSender.__init__(self)
        self.fixture_signal_queue = QueueReceiver[FixtureSignal](data_senders.get('fixture_signal_queue'))
        self.dmx_queue_sender = QueueSender[DmxSignal]("dmx")
        self.post_processing_finished_sender = NumpyArraySender(np.shape([1]))
        self.post_processors = self._instantiate_post_processors(data_senders)

    def delete(self):
        logging.info("Deleting post processors")
        for postprocessor in self.post_processors:
            postprocessor.delete()
        self.post_processing_finished_sender.close()
        self.fixture_signal_queue.close()
        self.dmx_queue_sender.close()
        super().delete()

    def _instantiate_post_processors(self, data_senders) -> list[PostProcessorBase]:
        postprocessor = []
        for postprocessor_class in PostProcessorBase.__subclasses__():
            postprocessor.append(postprocessor_class(data_senders))
        return postprocessor

    def run(self):
        logging.debug("Starting post processor run loop")
        while not self.kill_event.is_set():
            fixture_signals = self.fixture_signal_queue.get_all_present()
            if fixture_signals:
                dmx_signals = []
                for postprocessor in self.post_processors:
                    dmx_signals = postprocessor.run(fixture_signals, dmx_signals)
                for dmx_signal in dmx_signals:
                    self.dmx_queue_sender.update(dmx_signal)
                self.post_processing_finished_sender.update(np.array([1]))
        self.delete()

    def get_outbound_data_senders(self) -> dict[str, SmSender]:
        return {
            'dmx_queue': self.dmx_queue_sender,
            'post_processing_finished': self.post_processing_finished_sender
        }
