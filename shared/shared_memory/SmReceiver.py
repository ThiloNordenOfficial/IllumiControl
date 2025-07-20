from abc import abstractmethod
from typing import TypeVar, Generic, final, TYPE_CHECKING

if TYPE_CHECKING:
    from shared.shared_memory.SmSender import SmSender

T = TypeVar('T')


class SmReceiver(Generic[T]):

    def __init__(self, sender: 'SmSender', clazz: type['SmSender']):
        self.sender: T = sender.as_type(sender,clazz)
        self.sender.register_receiver(self)


    @final
    def delete(self):
        self.sender.unregister_receiver(self)
        self.close()

    @abstractmethod
    def close(self):
        pass
    abstractmethod(close)
