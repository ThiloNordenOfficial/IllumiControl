import time
from threading import Thread
from typing import Mapping

import numpy as np
import pyaudio
from hs_tasnet import HSTasNet


def callback(in_data: bytes | None, frame_count: int, time_info: Mapping[str, float],
             status: int) -> \
        tuple[bytes | None, int] | None:
    audio_data = np.frombuffer(in_data, dtype=np.float32)
    stems = transform_fn(audio_data.copy())  # shape: (channels, num_sources, chunk_len)
    print(f"shape: {np.shape(stems)}")
    return stems[0], pyaudio.paContinue


if __name__ == '__main__':
    file_type = '.wav'
    model = HSTasNet(small=True, stereo=False, sample_rate=16000).to('cuda')
    transform_fn = model.init_stateful_transform_fn('cuda', None, True, False)
    p = pyaudio.PyAudio()
    stream = p.open(
        rate=16000,
        format=pyaudio.paFloat32,
        channels=1,
        input=True,
        output=True,
        frames_per_buffer=512,
        input_device_index=7,
        output_device_index=7,
        stream_callback=callback,
    )
    try:
        stream.start_stream()
        while stream.is_active():
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping stream...")
        stream.stop_stream()
        stream.close()
        p.terminate()
