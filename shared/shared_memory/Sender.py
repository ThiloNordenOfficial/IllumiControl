from abc import abstractmethod, ABC
from typing import final, TypeVar, Generic, TYPE_CHECKING, Type, cast


T = TypeVar('T')
S = TypeVar('S', bound='Sender')

if TYPE_CHECKING:
    from shared.shared_memory.Receiver import Receiver


class Sender(Generic[T]):
    def __init__(self):
        self.receivers: list['Receiver'] = []

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
        if not isinstance(sender, clazz):
            raise TypeError(f"Expected sender to be an instance of {clazz.__name__}, got {type(sender).__name__}")
        return cast(S, sender)

    @final
    def delete(self):
        while self.receivers:
            receiver = self.receivers.pop()
            receiver.delete()
        self.close()

    def register_receiver(self, receiver: 'Receiver'):
        if receiver not in self.receivers:
            self.receivers.append(receiver)

    def unregister_receiver(self, receiver: 'Receiver'):
        if receiver in self.receivers:
            self.receivers.remove(receiver)
