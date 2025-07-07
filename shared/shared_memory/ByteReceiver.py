from shared.shared_memory.ByteSender import ByteSender
from shared.shared_memory.Receiver import Receiver
from shared.shared_memory.Sender import Sender


class ByteReceiver(Receiver[ByteSender]):
    def __init__(self, sender: Sender):
        super().__init__(sender, ByteSender)

    def read(self, size: int) -> bytes:
        return self.sender.read_last(size)


    def read_all(self):
        return self.read(self.sender.size)

    def close(self):
        self.sender.unregister_receiver(self)
        del self
