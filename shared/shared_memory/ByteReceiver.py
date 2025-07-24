import logging
from multiprocessing.shared_memory import SharedMemory

from shared.shared_memory.ByteSender import ByteSender
from shared.shared_memory.SmReceiver import SmReceiver
from shared.shared_memory.SmSender import SmSender


class ByteReceiver(SmReceiver[ByteSender]):
    def __init__(self, sender: SmSender):
        super().__init__(sender, ByteSender)
        self.sender = sender
        self.buffer = sender.shm.buf
        self.shm = SharedMemory(name=sender.shm.name)
        self.size = sender.size

    def read_last(self, length=None)-> bytes:
        if length is None:
            length = self.size
        if length > self.size:
            raise ValueError("Requested length exceeds buffer capacity")

        write_index = self.sender.write_index.value
        start = (write_index - length) % self.size
        if start < write_index:
            return bytes(self.buffer[start:write_index])
        else:
            return bytes(self.buffer[start:]) + bytes(self.buffer[:write_index])

    def close(self):
        self.sender.unregister_receiver(self)
        del self
