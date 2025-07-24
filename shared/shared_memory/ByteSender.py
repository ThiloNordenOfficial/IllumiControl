from multiprocessing import shared_memory, Value
from shared.shared_memory.SmSender import SmSender, T
import logging


class ByteSender(SmSender[bytes]):
    def __init__(self, size, shm_name=None):
        super().__init__()
        self.size = size
        self.shm = shared_memory.SharedMemory(create=True, size=size, name=shm_name)
        self.buffer = self.shm.buf
        self.write_index = Value('i', 0)  # Shared memory index for writing
        self.total_written = Value('i', 0)  # Used for tracking wrap-arounds

    def update(self, data: bytes):
        for byte in data:
            self.buffer[self.write_index.value % self.size] = byte
            self.write_index.value = (self.write_index.value + 1) % self.size
            self.total_written.value += 1

    def register_receiver(self, receiver):
        super().register_receiver(receiver)

    def unregister_receiver(self, receiver):
        super().unregister_receiver(receiver)

    def close(self):
        self.shm.close()
        self.shm.unlink()
        del self.shm
