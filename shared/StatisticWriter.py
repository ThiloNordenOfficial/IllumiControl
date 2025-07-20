import argparse
import logging
import os
from datetime import datetime
from typing import TextIO

from shared.CommandLineArgumentAdder import CommandLineArgumentAdder
from shared import GracefulKiller
from shared.validators.is_valid_file import is_valid_file


class StatisticWriter(GracefulKiller, CommandLineArgumentAdder):
    statistics_are_active: bool = False
    path = None

    def __init__(self):
        self._name = self.__class__.__name__
        self.path = self.path if self.path is not None else os.path.join(os.getcwd(), "statistics")
        if self.statistics_are_active:
            self._file_handle: TextIO = self._setup_statistics()

    def delete(self):
        self._file_handle.close()

    def _setup_statistics(self):
        os.makedirs(self.path, exist_ok=True)
        file_name = f"{self._name}.statistic.log"
        file_path = os.path.join(self.path, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
        return open(file_path, 'x')

    def write_statistics(self, time_taken: float):
        if self.statistics_are_active:
            time_taken_trimmed = "{:.6f}".format(time_taken)
            self._file_handle.write(f"{datetime.now()}, {time_taken_trimmed}\n",)
            self._file_handle.flush()

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        parser.add_argument("-stats", "--statistics", dest='statistics', default='False',
                            help="Enable writing statistics of extractors to file")
        parser.add_argument("-stats-path", "--statistics-path", dest='statistics_path', help="Path to the statistics folder")
        return parser

    @classmethod
    def apply_command_line_arguments(cls, args: argparse.Namespace):
        cls.statistics_are_active = args.statistics is not None and args.statistics == 'True'
        cls.path = args.statistics_path
