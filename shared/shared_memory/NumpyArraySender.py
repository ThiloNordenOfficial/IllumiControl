import numpy as np
from multiprocessing import shared_memory, Condition

from shared.shared_memory.SmSender import SmSender


def safe_create_shared_memory(name, size) -> shared_memory.SharedMemory:
    try:
        # Try to create new shared memory
        return shared_memory.SharedMemory(create=True, size=size, name=name)
    except FileExistsError:
        # If it exists, try to unlink it first
        try:
            existing_shm = shared_memory.SharedMemory(name=name)
            existing_shm.unlink()
            existing_shm.close()
        except:
            pass
        # Now try to create again
        return shared_memory.SharedMemory(create=True, size=size, name=name)


class NumpyArraySender(SmSender[np.ndarray]):
    """
    DataSender creates a shared memory block where a NumPy array along with a version number
    is stored. A Condition is used to notify receivers when an update occurs.
    """

    def __init__(self, shape, dtype=np.float64, shm_name=None):
        super().__init__()
        self.sender = self.__class__.__name__
        self.shape = shape
        self.dtype = np.dtype(dtype)
        self.data_nbytes = np.prod(shape) * self.dtype.itemsize
        # Total size: 8 bytes for the version number + data bytes
        self.total_size = 8 + self.data_nbytes

        # Create the shared memory block
        self.shm = safe_create_shared_memory(size=self.total_size, name=shm_name)

        self.name = self.shm.name
        # Create a NumPy view for the version number (first 8 bytes, as int64)
        self.version_array = np.ndarray((1,), dtype=np.int64, buffer=self.shm.buf[:8])
        self.version_array[0] = 0

        # Create a NumPy view for the actual data (from byte 8 onwards)
        self.data_array = np.ndarray(self.shape, dtype=self.dtype, buffer=self.shm.buf[8:])

        # Create a Condition to notify receivers of updates
        self.condition = Condition()

    def update(self, new_data):
        """
        Updates the array in shared memory and notifies all receivers.
        The new_data array must have the same shape as the initial array.
        """
        if new_data.shape != self.shape:
            raise ValueError(f"Shape mismatch: Expected {self.shape}, got {new_data.shape}")

        with self.condition:
            # Copy the new data into the shared memory array
            np.copyto(self.data_array, new_data)
            # Increment the version number
            self.version_array[0] += 1
            # Notify all waiting receivers
            self.condition.notify_all()
