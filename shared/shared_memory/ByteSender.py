from multiprocessing import shared_memory, Value, Manager
from shared.shared_memory.SmSender import SmSender, T


class ByteSender(SmSender[bytes]):
    def __init__(self, size, shm_name=None):
        super().__init__()
        manager = Manager()
        self.lock = manager.Lock()
        self.size = size
        self.shm = shared_memory.SharedMemory(create=True, size=size, name=shm_name)
        self.buffer = self.shm.buf
        self.write_index = Value('i', 0)  # Shared memory index for writing

    def update(self, data: bytes):
        with self.lock:
            if len(data) % 2 != 0:
                raise ValueError("Data length must be a multiple of 2 bytes for int16.")

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
        self.shm.close()
        self.shm.unlink()
        del self.shm
