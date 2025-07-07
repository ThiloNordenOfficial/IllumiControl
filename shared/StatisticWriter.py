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

    def __init__(self):
        self._name = self.__class__.__name__
        logging.error(
            f"Initializing StatisticWriter for {self._name} with statistics active: {self.statistics_are_active}")
        if self.statistics_are_active:
            logging.error(f"Statistics are active for {self._name}. Setting up file handle.")
            self._file_handle: TextIO = self._setup_statistics()

    def delete(self):
        self._file_handle.close()

    def _setup_statistics(self):
        file_name = f"{self._name}.statistic.log"
        file_path = os.path.join("statistics", file_name)
        return open(file_path, 'a')

    def write_statistics(self, data):
        if self.statistics_are_active:
            self._file_handle.write(f"{datetime.now()}: {data}\n")
            self._file_handle.flush()

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        parser.add_argument("-stats", "--statistics", dest='statistics', type=bool, default=False,
                            help="Enable writing statistics of extractors to file")
        parser.add_argument("-stats-path", "--statistics-path", dest='statistics_path', default="statistics",
                            type=lambda x: is_valid_file(parser, x), help="Path to the statistics folder")
        return parser

    @classmethod
    def apply_command_line_arguments(cls, args: argparse.Namespace):
        cls.statistics_are_active = args.statistics
