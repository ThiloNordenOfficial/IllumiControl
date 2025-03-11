from abc import abstractmethod
from threading import Event


class GracefulKiller(object):
    kill_event = Event()

    @abstractmethod
    def delete(self):
        pass

    delete = abstractmethod(delete)
