import logging
import numpy as np
from typing import Union, List, Tuple

from analyse.AnalyserBase import AnalyserBase
from shared.shared_memory import SmSender, NumpyArraySender, ByteReceiver, NumpyArrayReceiver


class StemLoudnessAnalyser(AnalyserBase):
    """Compute per-stem loudness (RMS in dB) from Demucs stems provided via ByteSender or NumpyArraySender.

    Looks for inbound senders whose key starts with "stem-" and attaches the appropriate receiver
    (ByteReceiver for ByteSender, NumpyArrayReceiver for NumpyArraySender).
    Publishes a single NumpyArraySender with shape (n_stems, 1) containing loudness in dB for each stem.
    """

    def __init__(self, inbound_data_senders: dict[str, SmSender]):
        super().__init__(inbound_data_senders)

        # Discover stem senders in the provided inbound_data_senders dict
        self.stem_keys = [k for k in inbound_data_senders.keys() if k.startswith("stem-")]
        self.stem_names = [k[len("stem-"):] for k in self.stem_keys]

        # Create receivers for each stem sender. Store tuples (name, receiver, kind)
        # kind is 'byte' or 'numpy'
        ReceiverType = Union[ByteReceiver, NumpyArrayReceiver]
        self.receivers: List[Tuple[str, ReceiverType, str]] = []
        for k in self.stem_keys:
            sender = inbound_data_senders.get(k)
            if sender is None:
                logging.warning(f"StemLoudnessAnalyser: no sender found for {k}")
                continue
            try:
                # Prefer numpy receiver if the sender is a NumpyArraySender
                if isinstance(sender, NumpyArraySender):
                    r = NumpyArrayReceiver(sender)
                    self.receivers.append((k, r, 'numpy'))
                else:
                    # Fallback to ByteReceiver for byte-based senders
                    r = ByteReceiver(sender)
                    self.receivers.append((k, r, 'byte'))
            except Exception as e:
                logging.warning(f"StemLoudnessAnalyser: failed to attach receiver for {k}: {e}")

        # Create one NumpyArraySender that will hold loudness values for all stems
        self.loudness_sender = NumpyArraySender(shape=(len(self.receivers), 1), dtype=np.float64)

    def get_outbound_data_senders(self) -> dict[str, SmSender]:
        return {
            "stems-loudness": self.loudness_sender,
        }

    async def run_procedure(self):
        # Read latest buffer for each stem and compute RMS loudness in dB
        loudness_values = []
        for name, r, kind in self.receivers:
            try:
                if kind == 'byte':
                    # ByteReceiver.read_last returns int16 numpy array
                    data = r.read_last()
                    if data is None:
                        data = np.array([], dtype=np.int16)
                    if data.size == 0:
                        loudness_values.append(-120.0)
                        continue
                    audio = data.astype(np.float32) / 32768.0

                else:  # 'numpy'
                    # NumpyArrayReceiver exposes a live view `data_array`; take a copy to avoid racing
                    try:
                        arr = r.data_array
                        data = np.array(arr, copy=True)
                    except Exception:
                        # If anything goes wrong, treat as no data
                        data = np.array([], dtype=np.float32)
                    if data.size == 0:
                        loudness_values.append(-120.0)
                        continue

                    # If integer dtype, convert accordingly
                    if np.issubdtype(data.dtype, np.integer):
                        # Assume int16 PCM
                        audio = data.astype(np.float32) / 32768.0
                    else:
                        # Assume float in -1..1
                        audio = data.astype(np.float32)

                # Compute RMS and dB
                if audio.size == 0:
                    loudness_values.append(-120.0)
                    continue
                rms = np.sqrt(np.mean(np.square(audio)))
                logging.warning(f"rms: {rms}")
                if rms <= 0.0 or not np.isfinite(rms):
                    db = -120.0
                else:
                    db = 20.0 * np.log10(rms)
                loudness_values.append(db)

            except Exception as e:
                logging.warning(f"StemLoudnessAnalyser: failed to read/process {name}: {e}")
                loudness_values.append(-120.0)

        # Pack into (n_stems, 1) and send
        if len(loudness_values) == 0:
            out = np.zeros((0, 1), dtype=np.float64)
        else:
            out = np.array(loudness_values, dtype=np.float64).reshape(-1, 1)

        try:
            logging.warning(f"loudness values: {out.flatten().tolist()}")
            self.loudness_sender.update(out)
        except Exception as e:
            logging.warning(f"StemLoudnessAnalyser: failed to update loudness sender: {e}")

    def delete(self):
        # Close receivers and sender
        for _name, r, _kind in getattr(self, 'receivers', []):
            try:
                r.close()
            except Exception:
                pass
        try:
            self.loudness_sender.close()
        except Exception:
            pass

