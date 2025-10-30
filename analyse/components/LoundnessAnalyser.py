import logging

import numpy as np

from analyse.AnalyserBase import AnalyserBase
from shared.shared_memory import SmSender, NumpyArraySender, NumpyArrayReceiver, ByteReceiver


class LoudnessAnalyser(AnalyserBase):
    def __init__(self, inbound_data_senders: dict[str, SmSender]):
        super().__init__(inbound_data_senders)
        self.raw_audio_data_receiver = ByteReceiver(inbound_data_senders.get("raw-audio-data"))
        self.loudness_sender = NumpyArraySender(shape=(1, 1))

    def get_outbound_data_senders(self) -> dict[str, SmSender]:
        return {
            "loudness-data": self.loudness_sender,
        }


    async def run_procedure(self):
        data = self.raw_audio_data_receiver.read_last(1000) # last eight of a second
        rms = np.sqrt(np.mean(data.astype(np.float32) ** 2))
        loudness_db = 20 * np.log10(rms)
        self.loudness_sender.update(np.array([[loudness_db]]))