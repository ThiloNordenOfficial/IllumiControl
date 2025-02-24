import logging

import numpy as np
import multiprocessing.shared_memory as shm


class AudioDataReceiver:
    def __init__(self, name, shape, dtype=np.float64):
        self.shape = shape
        self.dtype = dtype
        self.shm = shm.SharedMemory(name=name)
        self.array = np.ndarray(shape, dtype=dtype, buffer=self.shm.buf)
        logging.debug("Initialized audio data receiver")

    def read_array(self):
        logging.debug("Reading array")
        return np.copy(self.array)

    def close(self):
        self.shm.close()
