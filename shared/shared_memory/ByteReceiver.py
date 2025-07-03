from shared.shared_memory.ByteSender import ByteSender
from shared.shared_memory.Receiver import Receiver
from shared.shared_memory.Sender import Sender


class ByteReceiver(Receiver[ByteSender]):
    def __init__(self, sender: Sender):
        super().__init__(sender, ByteSender)
        self.max_size = self.sender.max_size

    def read_new(self) -> bytes:
        """Read new data for this receiver from the sender's stream."""
        return self.sender.get_receiver_stream(self)

    def close(self):
        # TODO document why this method is empty
        pass
