from shared.shared_memory.ByteSender import ByteSender
from shared.shared_memory.SmReceiver import SmReceiver
from shared.shared_memory.SmSender import SmSender


class ByteReceiver(SmReceiver[ByteSender]):
    def __init__(self, sender: SmSender):
        super().__init__(sender, ByteSender)

    def read(self, size: int) -> bytes:
        return self.sender.read_last(size)


    def read_all(self):
        return self.read(self.sender.size)

    def close(self):
        self.sender.unregister_receiver(self)
        del self
