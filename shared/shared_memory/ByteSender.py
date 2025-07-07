from threading import Lock
from shared.shared_memory.LimitedBytesIO import LimitedBytesIO
from shared.shared_memory.Sender import Sender, T
import logging


class ByteSender(Sender[bytes]):
    def __init__(self, max_size):
        super().__init__()
        self.sender = self.__class__.__name__
        self.max_size = max_size
        self.byte_stream = LimitedBytesIO(max_size)
        self._lock = Lock()
        self._receiver_positions = {}

    def update(self, new_data: bytes):
        n = len(new_data)
        if n > self.max_size:
            raise ValueError(f"Data too large for ring buffer: {n} > {self.max_size}")
        with self._lock:
            self.byte_stream.write(new_data)
            self.byte_stream.flush()
            # Reset all receiver positions to 0 if buffer was truncated
            for receiver in self._receiver_positions:
                if self.byte_stream.tell() < self._receiver_positions[receiver]:
                    # logging.error(f"ByteSender: resetting receiver {id(receiver)} position to 0 due to truncation")
                    self._receiver_positions[receiver] = 0

    def register_receiver(self, receiver):
        with self._lock:
            self._receiver_positions[receiver] = 0
        logging.info(f"ByteSender.register_receiver: Registered receiver {id(receiver)}.")
        super().register_receiver(receiver)

    def unregister_receiver(self, receiver):
        with self._lock:
            if receiver in self._receiver_positions:
                del self._receiver_positions[receiver]
        logging.info(f"ByteSender.unregister_receiver: Unregistered receiver {id(receiver)}.")
        super().unregister_receiver(receiver)

    def get_receiver_stream(self, receiver):
        """Return a view of the stream for the receiver, starting at its last read position."""
        pos = self._receiver_positions.get(receiver, 0)
        self.byte_stream.seek(pos)
        data = self.byte_stream.read()
        self._receiver_positions[receiver] = self.byte_stream.tell()
        logging.error(f"Position for receiver {id(receiver)} updated to {self._receiver_positions[receiver]}.")
        # logging.info(f"ByteSender.get_receiver_stream: Receiver {id(receiver)} read {len(data)} bytes from position {pos}.")
        return data

    def close(self):
        self.byte_stream.close()
