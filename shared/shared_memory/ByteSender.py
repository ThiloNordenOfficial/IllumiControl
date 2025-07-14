import threading
from multiprocessing import shared_memory
from shared.shared_memory.SmSender import SmSender, T
import logging


class ByteSender(SmSender[bytes]):
    def __init__(self, size, shm_name=None):
        super().__init__()
        self.size = size
        self.lock = threading.Lock()
        self.shm = shared_memory.SharedMemory(create=True, size=size, name=shm_name)
        self.buffer = self.shm.buf
        self.write_index = 0
        self.total_written = 0  # Used for tracking wrap-arounds

    def update(self, data: bytes):
        with self.lock:
            for byte in data:
                self.buffer[self.write_index % self.size] = byte
                self.write_index = (self.write_index + 1) % self.size
                self.total_written += 1

    def read_last(self, length=None):
        if length is None:
            length = self.size
        with self.lock:
            if length > self.size:
                raise ValueError("Requested length exceeds buffer capacity")

            start = (self.write_index - length) % self.size
            if start < self.write_index:
                return bytes(self.buffer[start:self.write_index])
            else:
                return bytes(self.buffer[start:]) + bytes(self.buffer[:self.write_index])

    def register_receiver(self, receiver):
        super().register_receiver(receiver)

    def unregister_receiver(self, receiver):
        super().unregister_receiver(receiver)

    def close(self):
        self.shm.close()
        self.shm.unlink()
        del self.shm
