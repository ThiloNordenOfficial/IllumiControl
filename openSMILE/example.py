import math

import opensmile
import pyaudio
import numpy as np
import time

def __init__(self):
    pass

def main(chunk_size, analyse_duration) -> (float, int):
    CHUNKSIZE = chunk_size  # fixed chunk size
    DEVICE_INDEX = 5

    # initialize portaudio

    p = pyaudio.PyAudio()

    # for i in range(p.get_device_count()):
    #     print(p.get_device_info_by_index(i))
    detected_sample_rate = p.get_device_info_by_index(DEVICE_INDEX)['defaultSampleRate']
    if detected_sample_rate.is_integer():
        sampling_rate = int(detected_sample_rate)
    else:
        sampling_rate = int(math.floor(detected_sample_rate))

    stream = p.open(format=pyaudio.paInt16, channels=1, rate=sampling_rate, input=True, frames_per_buffer=CHUNKSIZE,
                    input_device_index=DEVICE_INDEX)

    smile = opensmile.Smile(
        feature_set=opensmile.FeatureSet.eGeMAPSv01b,
        multiprocessing=True
    )
    print(smile.feature_names)
    amount_parameters = len(smile.feature_names)
    t_end = time.time() + analyse_duration  # Run for 5 seconds
    calc_durations = []

    # do this as long as you want fresh samples
    while time.time() < t_end:
        stream_data = stream.read(CHUNKSIZE)
        numpydata = np.frombuffer(stream_data, dtype=np.int16)
        start_time = time.time()
        calculated_data = smile.process_signal(
            numpydata,
            sampling_rate
        )
        calc_durations.append(time.time() - start_time)

    # close stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    return sum(calc_durations) / len(calc_durations), amount_parameters


if __name__ == "__main__":
    # analyse_duration = 30
    #
    # chunk_sizes = []
    # for i in range(10, 20):
    #     chunk_sizes.append(2 ** i)
    #
    # runtimes = []
    # for chunk_size in chunk_sizes:
    #     runtimes.append((chunk_size, main(chunk_size, analyse_duration), chunk_size / 16000 * 100))
    #
    # for runtime in runtimes:
    #     print(runtime)
    main(8192, 30)