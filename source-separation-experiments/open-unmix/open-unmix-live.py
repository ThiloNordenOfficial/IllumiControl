import time
from typing import Mapping
import openunmix
import numpy as np
import pyaudio
import torch


def callback(in_data: bytes | None, frame_count: int, time_info: Mapping[str, float],
             status: int) -> \
        tuple[bytes | None, int] | None:
    np_audio = np.frombuffer(in_data, dtype=np.float32)
    tensor_audio = torch.tensor(np_audio, dtype=torch.float32)
    umx_audio = openunmix.utils.preprocess(tensor_audio, sample_rate, separator.sample_rate)
    print(separator.sample_rate)
    audio = umx_audio.to('cuda')

    start_time = time.time()
    stems = separator(audio)
    end_time = time.time()

    print(f"Processing time: {end_time - start_time:.4f} seconds")

    source = stems[0, replay_stem, 0].detach().cpu().numpy()

    return source.tobytes(), pyaudio.paContinue


if __name__ == '__main__':
    model = openunmix.umxhq
    #model = openunmix.umxl
    separator = model(device='cuda', pretrained=True, wiener_win_len=None, niter=1)
    print(separator)

    stem = {
        "vocals": 0,
        "drums": 1,
        "bass": 2,
        "other": 3
    }
    replay_stem = stem['vocals']
    p = pyaudio.PyAudio()
    sample_rate = 44100
    stream = p.open(
        rate=sample_rate,
        format=pyaudio.paFloat32,
        channels=1,
        input=True,
        output=True,
        frames_per_buffer=4096,
        input_device_index=21,
        output_device_index=21,
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
