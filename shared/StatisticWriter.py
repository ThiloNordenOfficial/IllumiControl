import logging
import os
from typing import TextIO

from shared import GracefulKiller


class StatisticWriter(GracefulKiller):
    statistics_are_active = False

    def __init__(self):
        """
        Initialize the StatisticWriter. This class is used to write statistics to a file.
        """
        self.statistics_are_active = logging.getLogger().getEffectiveLevel() == logging.DEBUG
        self._extractor_name = self.__class__.__name__
        if self.statistics_are_active:
            self._file_handle: TextIO = self._setup_statistics()

    def delete(self):
        self._file_handle.close()

    def _setup_statistics(self):
        file_name = f"{self._extractor_name}.statistic.log"
        file_path = os.path.join("statistics", file_name)
        return open(file_path, 'a')

    def write_statistics(self, data):
        """
        Write the analytics data to the file. This method is called every time a new frame is received.
        :param data: The time it took to generate and extract.
        """
        if self.statistics_are_active:
            self._file_handle.write(f"{data}\n")
            self._file_handle.flush()
