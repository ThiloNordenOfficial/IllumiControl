import math
import opensmile
import pyaudio
import numpy as np
import time


def main(chunk_size, analyse_duration) -> (float, int, list):
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
    print(sampling_rate, chunk_size, DEVICE_INDEX)
    smile = opensmile.Smile(
        feature_set="./configs/compare/ComParE_2016.conf",
        multiprocessing=True,
        num_workers=4
    )
    amount_parameters = len(smile.feature_names)
    t_end = time.time() + analyse_duration  # Run for 5 seconds
    calc_durations = []

    # do this as long as you want fresh samples
    shapes = []
    while time.time() < t_end:
        stream_data = stream.read(CHUNKSIZE)
        numpydata = np.frombuffer(stream_data, dtype=np.int16)
        start_time = time.time()
        shapes.append(smile.process_signal(
            numpydata,
            sampling_rate
        ).to_numpy().shape)
        calc_durations.append(time.time() - start_time)

    # close stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    return sum(calc_durations) / len(calc_durations), amount_parameters, shapes


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
    print(main(16384, 30))
