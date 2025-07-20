from multiprocessing import shared_memory

import numpy as np

from shared.shared_memory import SmSender
from shared.shared_memory.NumpyArraySender import NumpyArraySender
from shared.shared_memory.SmReceiver import SmReceiver


class NumpyArrayReceiver(SmReceiver[NumpyArraySender]):
    """
    DataReceiver connects to the shared memory block created by DataSender and waits
    for updates using a shared Condition. When an update occurs, it returns the updated array.
    """

    def __init__(self, sender: SmSender):
        super().__init__(sender, NumpyArraySender)
        self.shape = self.sender.shape
        self.dtype = np.dtype(self.sender.dtype)
        self.data_size = np.prod(self.shape) * self.dtype.itemsize
        self.total_size = 8 + self.data_size

        # Connect to the existing shared memory block
        self.shm = shared_memory.SharedMemory(name=self.sender.shm.name)
        self.version_array = np.ndarray((1,), dtype=np.int64, buffer=self.shm.buf[:8])
        self.data_array = np.ndarray(self.shape, dtype=self.dtype, buffer=self.shm.buf[8:])

        # Store the last read version number
        self.last_version = self.version_array[0]
        self.condition = self.sender.condition

    def read_on_update(self, timeout: float = None) -> np.ndarray:
        """
        Blocks until an update from DataSender occurs (i.e., the version number changes),
        then returns a copy of the updated array.
        """
        with self.condition:
            successful = self.condition.wait_for(lambda: self.version_array[0] != self.last_version, timeout)
            if not successful:
                raise TimeoutError()
            self.last_version = self.version_array[0]

        return self.data_array

    def close(self):
        """
        Closes the shared memory connection.
        """
        self.sender.unregister_receiver(self)
        self.shm.close()
        del self
