import logging
from multiprocessing.shared_memory import SharedMemory

import numpy as np

from shared.shared_memory.ByteSender import ByteSender
from shared.shared_memory.SmReceiver import SmReceiver
from shared.shared_memory.SmSender import SmSender


class ByteReceiver(SmReceiver[ByteSender]):
    def __init__(self, sender: SmSender):
        super().__init__(sender, ByteSender)
        self.lock = self.sender.lock
        self.shm = SharedMemory(name=self.sender.shm.name)
        self.buffer = self.shm.buf
        self.size = self.sender.size
        self.dtype = np.dtype(self.sender.dtype)

    def read_last(self, length=None) -> np.ndarray:
        with self.lock:
            if length is None:
                length = self.size
            if length > self.size:
                raise ValueError("Requested length exceeds buffer capacity")

            write_index = self.sender.write_index.value
            start = (write_index - length) % self.size
            itemsize = self.dtype.itemsize
            if start < write_index:
                bytes_available = write_index - start
            else:
                bytes_available = (self.size - start) + write_index

            bytes_to_read = min(length, bytes_available)
            elements_to_read = bytes_to_read // itemsize
            actual_bytes = elements_to_read * itemsize

            if actual_bytes == 0:
                return np.array([], dtype=self.dtype)

            if start + actual_bytes <= self.size:
                byte_data = bytes(self.buffer[start:start + actual_bytes])
            else:
                first_part_size = self.size - start
                first_part = self.buffer[start:self.size]
                second_part = self.buffer[:actual_bytes - first_part_size]
                byte_data = bytes(first_part) + bytes(second_part)

            return np.frombuffer(byte_data, dtype=self.dtype)
    def close(self):
        self.sender.unregister_receiver(self)
        del self
