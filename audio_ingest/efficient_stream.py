import time

import numpy as np
import opensmile
from opensmile import FeatureLevel

from audio_ingest import AudioProvider

if __name__ == "__main__":
    smile = opensmile.Smile(
        feature_set="./configs/compare/ComParE_2016.conf",
        feature_level=FeatureLevel.Functionals
    )

    ap = AudioProvider(5, 16000, 1048576, 1)

    t_end = time.time() + 5  # Run for 5 seconds
    while time.time() < t_end:
        start_time = time.time()
        stream_data = ap.stream.read(1048576)
        numpydata = np.frombuffer(stream_data, dtype=np.int16)
        print(f"Time to read stream data: {time.time() - start_time}")
        start_time = time.time()
        data = smile.process_signal(
            np.frombuffer(
                numpydata,
                dtype=np.int16
            ),
            ap.sample_rate
        ).to_numpy()
        print(f"Time to process signal: {time.time() - start_time}")
