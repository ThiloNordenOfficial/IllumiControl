import logging
from typing import TypeVar

from ipcqueue.posixmq import Queue

from shared.shared_memory.SmSender import SmSender

T = TypeVar('T')


class QueueSender[T](SmSender[T]):
    _queues = {}

    def __init__(self, name: str, maxsize: int = 10, maxmsgsize: int = 1024):
        super().__init__()
        self.name = name
        self.maxsize = maxsize
        self.maxmsgsize = maxmsgsize
        if self.name not in QueueSender._queues:
            logging.debug(f"QueueSender: Creating new queue for {self.name}, maxsize={maxsize}, maxmsgsize={maxmsgsize}")
            QueueSender._queues[self.name] = Queue(self.name, maxsize=maxsize, maxmsgsize=maxmsgsize)
        self.queue: Queue = QueueSender._queues[self.name]


    def close(self):
        self.queue.close()
        self.queue.unlink()

    def update(self, new_data: T):
        if self.queue.qsize() >= self.maxsize:
            logging.warning(f"QueueSender: Queue {self.name} is full, dropping oldest data")
            self.queue.get_nowait()
        self.queue.put(new_data, False)

