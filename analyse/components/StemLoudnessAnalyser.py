import asyncio
import logging
import math
import time

import librosa.feature
import numpy as np

from analyse.TimingProviderBase import TimingProviderBase
from shared.shared_memory import SmSender, QueueReceiver, NumpyArraySender, NumpyArrayReceiver, ByteReceiver


class StemLoudnessAnalyser(TimingProviderBase):
    def __init__(self, inbound_data_senders: dict[str, SmSender]):
        self.timing_sender = NumpyArraySender(shape=np.shape(np.array((1.,))), dtype=np.float64)
        inbound_data_senders.update([("timing-data", self.timing_sender)])
        super().__init__(inbound_data_senders)

        self.stem_senders = {k.split("separated_audio_")[1]: inbound_data_senders[k] for k in
                             inbound_data_senders.keys() if
                             k.startswith("separated_audio_")}
        self.stem_receivers = {stem: ByteReceiver(sender) for stem, sender in self.stem_senders.items()}
        self.samples_per_frame = math.ceil(1 / self.fps * 44100 * np.dtype(np.float32).itemsize)

        self.data_senders: dict[str, SmSender] = {
            f"stem_loudness_{stem}": NumpyArraySender(shape=(1,), dtype=np.float64) for stem, _ in
            self.stem_senders.items()
        }

    def get_outbound_data_senders(self) -> dict[str, SmSender]:
        return self.data_senders

    async def run_procedure(self):
        for name, receiver in self.stem_receivers.items():
            stem_audio = receiver.read_last(self.samples_per_frame)
            if len(stem_audio) <= 1:
                continue
            track_rms = librosa.feature.rms(y=stem_audio, center=False).mean()
            # TODO worauf basiert librosa die rms?
            logging.debug(f"RMS for {name}: {track_rms*1000}")
            self.data_senders[f"stem_loudness_{name}"].update(np.asarray([track_rms*1000]))
        await asyncio.sleep(1 / self.fps)
        self.timing_sender.update(np.array([1 / self.fps]))

    def delete(self):
        for name, sender in self.data_senders.items():
            sender.close()
            sender.delete()
