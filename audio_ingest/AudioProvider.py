import logging

import pyaudio


class AudioProvider:
    def __init__(self, device_index: int, sample_rate=None):
        self.p = pyaudio.PyAudio()
        logging.debug(f"Opening audio stream with device index {device_index}")

    @staticmethod
    def list_devices():
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            print(p.get_device_info_by_index(i))
    list_devices = staticmethod(list_devices)
