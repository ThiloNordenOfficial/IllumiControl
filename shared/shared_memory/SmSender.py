import logging
from abc import abstractmethod
from typing import final, TypeVar, Generic, TYPE_CHECKING, Type, cast


T = TypeVar('T')
S = TypeVar('S', bound='SmSender')

if TYPE_CHECKING:
    from shared.shared_memory.SmReceiver import SmReceiver


class SmSender(Generic[T]):
    def __init__(self):
        self.receivers: list['SmReceiver'] = []

    @abstractmethod
    def close(self):
        pass

    abstractmethod(close)

    @abstractmethod
    def update(self, new_data: T):
        pass

    abstractmethod(update)

    @staticmethod
    def as_type(sender: object, clazz: Type[S]) -> S:
        if not sender:
            raise ValueError("Sender instance must be provided")
        check_type = getattr(clazz, "__origin__", clazz)
        if not isinstance(sender, check_type):
            raise TypeError(f"Expected sender to be an instance of {clazz.__name__}, got {type(sender).__name__}")
        return cast(S, sender)

    @final
    def delete(self):
        while self.receivers:
            receiver = self.receivers.pop()
            receiver.delete()
        self.close()

    def register_receiver(self, receiver: 'SmReceiver'):
        if receiver not in self.receivers:
            logging.debug(f"{self.__class__.__name__}.register_receiver: Registered receiver {id(receiver)}.")
            self.receivers.append(receiver)

    def unregister_receiver(self, receiver: 'SmReceiver'):
        if receiver in self.receivers:
            logging.debug(f"{self.__class__.__name__}.unregister_receiver: Unregistered receiver {id(receiver)}.")
            self.receivers.remove(receiver)
