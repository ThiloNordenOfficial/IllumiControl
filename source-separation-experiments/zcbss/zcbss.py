import logging

import librosa
import numpy as np
from matplotlib import pyplot as plt
from scipy.io import wavfile

from jns import jns

def zcbss_multiple_instruments(audio_stream, frame_size, overlap, num_instruments):
    """
    Implements the Zero-Crossing Based Source Separation (ZCBSS) algorithm for a specified number of instruments.

    Args:
        audio_stream (numpy.ndarray): The continuous audio stream.
        frame_size (int): The size of each frame of data.
        overlap (int): The number of samples that overlap between consecutive frames.
        num_instruments (int): The number of instruments in the audio stream.

    Returns:
        list of numpy.ndarray: The separated continuous audio streams for each instrument as numpy arrays.
    """

    # Divide the continuous audio stream into overlapping frames
    frames = [audio_stream[i:i+frame_size] for i in range(0, len(audio_stream)-frame_size+1, frame_size-overlap)]
    # Initialize the list of separated sources
    separated_sources = []

    # Iteratively separate the sources
    while len(frames) > 0:
        # Get the first two frames of data
        x1 = frames.pop(0)
        x2 = frames.pop(0)

        # Apply ZCBSS to separate the sources
        s1, s2 = zcbss(x1, x2)

        # Add the separated sources to the list
        separated_sources.append(s1)
        separated_sources.append(s2)

        # If we have separated the specified number of sources, stop iterating
        if len(separated_sources) >= num_instruments:
            break

        # Use one of the separated sources as a new frame of data
        frames.append(s2)

    # Combine the separated sources using overlap-add
    separated_sources = np.array(separated_sources)
    # logging.error(separated_sources)
    for i in range(0,len(separated_sources)):
        logging.error(len(separated_sources[i]))
        wavfile.write(f'instrument_{i}.wav', 44100, separated_sources[i])

    return separated_sources

def zcbss(x1, x2):
    """
    Implements the Zero-Crossing Based Source Separation (ZCBSS) algorithm.

    Args:
        x1 (numpy.ndarray): The first convolved mixed signal.
        x2 (numpy.ndarray): The second convolved mixed signal.

    Returns:
        tuple: A tuple containing the separated signals s1 and s2 as numpy arrays.
    """

    # 1: Calculate X'1(n) and X'2(n)
    n = np.arange(len(x1))
    X1_prime = x1 - 2 * x1[np.maximum(0, n - 1)]  # Handle boundary conditions
    X2_prime = x2 - 2 * x2[np.maximum(0, n - 1)]  # Handle boundary conditions

    # 2: Calculate V1(n) and V2(n) using JADE
    # Prepare data for JADE.  JADE expects a matrix where each column is a mixed signal.
    X = np.vstack((X1_prime, X2_prime))

    # Run JADE
    B, S = jns.jade(X)

    V1 = S[0, :]
    V2 = S[1, :]

    # 3: Calculate s1(n) and s2(n)
    s1 = V1 + 2 * np.roll(V1, -1)  # Equivalent to V1(n) + 2s1(n+1)
    s2 = V2 + 2 * np.roll(V2, -1)  # Equivalent to V2(n) + 2s2(n+1)

    return s1, s2


# Example Usage (and testing)
if __name__ == '__main__':
    fs = 44100
    duration = 1
    freqs = [440, 880, 1760]  # A4, A5, A6

    segments = []
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)

    for f in freqs:
        seg = 0.5 * np.sin(2 * np.pi * f * t)
        segments.append(seg)

    signal = np.concatenate(segments)

    signal_int16 = np.int16(signal * 32767)
    wavfile.write("sample_audio.wav", fs, signal_int16)
    sample_rate, audio_stream = wavfile.read('Jennifer.wav')

    # Separate the audio stream into tracks for each instrument
    separated_audio_streams = zcbss_multiple_instruments(audio_stream, frame_size=1024, overlap=512, num_instruments=3)
    # logging.error(separated_audio_streams)

    # Save the separated audio streams as WAV files
    for i, stream in enumerate(separated_audio_streams):
        wavfile.write(f'{i + 1}.wav', sample_rate, stream)
        pass

