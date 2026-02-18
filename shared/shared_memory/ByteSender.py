from multiprocessing import shared_memory, Value, Manager

import numpy as np
from numpy import ndarray

from shared.shared_memory.SmSender import SmSender, T


def get_or_create_shared_memory(name, size) -> shared_memory.SharedMemory:
    try:
        return shared_memory.SharedMemory(size=size, name=name)
    except FileNotFoundError:
        return shared_memory.SharedMemory(create=True, size=size, name=name)


class ByteSender(SmSender[bytes]):
    def __init__(self, size, shm_name=None, dtype=np.int16):
        super().__init__()
        manager = Manager()
        self.lock = manager.Lock()
        self.size = size
        self.dtype = dtype
        self.shm = get_or_create_shared_memory(shm_name, size)
        self.buffer = self.shm.buf
        self.write_index = Value('i', 0)  # Shared memory index for writing

    def update(self, data: bytes):
        with self.lock:
            start = self.write_index.value % self.size
            end = (self.write_index.value + len(data)) % self.size
            if end < start:
                self.buffer[start:] = data[:self.size - start]
                self.buffer[:end] = data[self.size - start:]
            else:
                self.buffer[start:end] = data
            self.write_index.value = end

    def register_receiver(self, receiver):
        super().register_receiver(receiver)

    def unregister_receiver(self, receiver):
        super().unregister_receiver(receiver)

    def close(self):
        super().close()
        self.shm.close()
        self.shm.unlink()
        del self.shm
