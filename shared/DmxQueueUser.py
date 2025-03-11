from ipcqueue.posixmq import Queue

from shared import GracefulKiller


class DmxQueueUser(GracefulKiller):
    def delete(self):
        self.dmx_queue.close()

    def __init__(self):
        self.dmx_queue = Queue("/dmx_queue")
