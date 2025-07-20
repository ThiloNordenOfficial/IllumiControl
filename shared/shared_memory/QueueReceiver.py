from typing import TypeVar

from ipcqueue.posixmq import Queue

from shared.shared_memory import SmReceiver, SmSender
from shared.shared_memory.QueueSender import QueueSender

T = TypeVar('T')

class QueueReceiver[T](SmReceiver[T]):
    def __init__(self, sender: SmSender):
        super().__init__(sender, QueueSender[T])
        self.queue = Queue(sender.name)

    def close(self):
        self.sender.unregister_receiver(self)
        self.queue.close()
        del self

    def get(self) -> T:
        return self.queue.get()

    def get_all_present(self)-> list[T]:
        signals = []
        while self.queue.qsize() != 0:
            signals.append(self.queue.get_nowait())
        return signals