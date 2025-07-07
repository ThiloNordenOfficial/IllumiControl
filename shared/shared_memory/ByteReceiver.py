from shared.shared_memory.ByteSender import ByteSender
from shared.shared_memory.Receiver import Receiver
from shared.shared_memory.Sender import Sender
import logging


class ByteReceiver(Receiver[ByteSender]):
    def __init__(self, sender: Sender):
        super().__init__(sender, ByteSender)
        self.max_size = self.sender.max_size
        self.sender.register_receiver(self)

    def read_new(self) -> bytes:
        return self.sender.get_receiver_stream(self)

    def close(self):
        # TODO document why this method is empty
        pass
