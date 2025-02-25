import numpy as np
from multiprocessing import shared_memory
from shared.shared_memory import NumpyArraySender


class NumpyArrayReceiver:
    """
    DataReceiver connects to the shared memory block created by DataSender and waits
    for updates using a shared Condition. When an update occurs, it returns the updated array.
    """

    def __init__(self, nps: NumpyArraySender):
        self.shape = nps.shape
        self.dtype = np.dtype(nps.dtype)
        self.data_size = np.prod(self.shape) * self.dtype.itemsize
        self.total_size = 8 + self.data_size

        # Connect to the existing shared memory block
        self.shm = shared_memory.SharedMemory(name=nps.shm.name)
        self.version_array = np.ndarray((1,), dtype=np.int64, buffer=self.shm.buf[:8])
        self.data_array = np.ndarray(self.shape, dtype=self.dtype, buffer=self.shm.buf[8:])

        # Store the last read version number
        self.last_version = self.version_array[0]
        self.condition = nps.condition

    def read_on_update(self) -> np.ndarray:
        """
        Blocks until an update from DataSender occurs (i.e., the version number changes),
        then returns a copy of the updated array.
        """
        with self.condition:
            self.condition.wait_for(lambda: self.version_array[0] != self.last_version)
            self.last_version = self.version_array[0]

        # TODO Think about returning a reference instead of a copy, to save time and memory
        return self.data_array.copy()

    def close(self):
        """
        Closes the shared memory connection.
        """
        self.shm.close()
