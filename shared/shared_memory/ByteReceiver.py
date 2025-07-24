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

    def read_last(self, length=None) -> np.ndarray:
        with self.lock:
            if length is None:
                length = self.size
            if length > self.size:
                raise ValueError("Requested length exceeds buffer capacity")

            write_index = self.sender.write_index.value
            start = (write_index - length) % self.size
            if start < write_index:
                byte_data = bytes(self.buffer[start:write_index])
            else:
                byte_data = bytes(self.buffer[start:]) + bytes(self.buffer[:write_index])
            return np.frombuffer(byte_data, dtype=np.int16)

    def close(self):
        self.sender.unregister_receiver(self)
        del self
