import logging

import numpy as np
import multiprocessing.shared_memory as shm
from multiprocessing import Event


class AudioDataSender:
    def __init__(self, shape, dtype=np.float64):
        self.shape = shape
        self.dtype = dtype
        self.size = np.prod(shape)
        self.shm = shm.SharedMemory(create=True, size=self.size * np.dtype(dtype).itemsize)
        self.name = self.shm.name
        self.array = np.ndarray(shape, dtype=dtype, buffer=self.shm.buf)
        self.update_event = Event()

    def update_data(self, new_data):
        if new_data.shape != self.shape:
            self.close()
            raise ValueError("New data must have the same shape as the original array")
        np.copyto(self.array, new_data)
        logging.debug("Updated data")
        self.update_event.set()
        self.update_event.clear()

    def close(self):
        self.shm.close()
        self.shm.unlink()
