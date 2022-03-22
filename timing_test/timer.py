from typing import Dict, Tuple, Any, Iterator, List, Callable, Union
from dataclasses import dataclass
from timeit import timeit
import csv
from os import path

import threading
import sys
import _thread as thread
import logging

from timing_test.print_out import PrintOut


@dataclass
class TimerSettings:
    test_name: str = 'unnamed'

    timeout: float = 60
    timeout_key: str = ''

    max_depth: int = 30

    re_runs: int = 5

    re_build_table: bool = False

    save_location: Tuple[str, ...] = tuple(['results'])


def main():
    pass


def exit_after(s):
    def outer(fn):
        def inner(*args, **kwargs):
            timer = threading.Timer(s, quit_function)
            timer.start()
            try:
                result = fn(*args, **kwargs)
            except KeyboardInterrupt:
                result = None
            finally:
                timer.cancel()
            return result

        return inner

    return outer


def quit_function():
    sys.stderr.flush()  # Python 3 stderr is likely buffered.
    thread.interrupt_main()  # raises KeyboardInterrupt


class Timer:
    def __init__(self, settings: TimerSettings, tests: List[str], algorithms: Dict[str, Callable], printer: PrintOut = PrintOut()):
        self.settings = settings
        self.tests = tests
        self.algorithms = algorithms
        self.printer = printer
        self.printer.show_key()

        self.past_header: List[str] = []
        self.past_results: Dict[str, List[str]] = {}
        self.results: Dict[str, List[Union[float, str]]] = {}

    def run(self):
        self.set_up_class()

        self._load_past_results()
        self._merge_past_results()

        self.printer.start_up()
        for run_index in range(self.settings.re_runs):  # this is done instead of changing the number on timeit to spread out the tests
            for test_index, test in enumerate(self.tests):
                input_data_for_test = self.set_up(test)
                for index, varying_input_data_for_test in self.generate_varying_input_data_for_test():
                    for algorithm_name, algorithm in self.algorithms.items():
                        testable_method = self.algorithm_wrapper(algorithm, **input_data_for_test, **varying_input_data_for_test)
                        if not self.has_timed_out_before(algorithm_name, **input_data_for_test, **varying_input_data_for_test):
                            # to handle detecting timeouts run the test in a separate thread
                            @exit_after(self.settings.timeout)
                            def time_out_method(method):
                                return timeit(method, number=1)

                            result = time_out_method(testable_method)

                            if result is None:  # Fail: test took too long
                                logging.info(f'TIMER : {algorithm_name} timed out.')
                                self.add_result_to_results(run_index, algorithm_name, self.settings.timeout_key, **input_data_for_test,
                                                           **varying_input_data_for_test)
                            else:  # Success: save result!
                                logging.info(f'TIMER : {algorithm_name} ran for {round(result, 3)}s.')
                                self.add_result_to_results(run_index, algorithm_name, result, **input_data_for_test,
                                                           **varying_input_data_for_test)
                                if run_index + 1 == self.settings.re_runs and test_index + 1 == len(self.tests):
                                    self.aggregate_results(algorithm_name, **input_data_for_test, **varying_input_data_for_test)
                        else:  # Fail: test failed in the past
                            self.add_result_to_results(run_index, algorithm_name, self.settings.timeout_key, **input_data_for_test,
                                                       **varying_input_data_for_test)

                    self.printer.depth(2)
                self.printer.depth(1)
            self.printer.depth(0)
        self._save_data()

    @classmethod
    def set_up_class(cls):
        pass

    @staticmethod
    def set_up(test: str) -> Dict[str, Any]:
        return {}

    @staticmethod
    def generate_varying_input_data_for_test() -> Iterator[Tuple[int, Dict[str, Any]]]:
        for i in range(1, 3):
            yield i, {'depth': i}

    @staticmethod
    def add_result_to_results(run_index: int, algorithm_name: str, result: Union[str, float], **input_data):
        pass

    @staticmethod
    def aggregate_results(algorithm_name: str, **input_data):
        pass

    @staticmethod
    def algorithm_wrapper(algorithm: Callable, **kwargs) -> Callable:
        return algorithm

    @staticmethod
    def is_timing_required(algorithm_name: str):
        return True

    @staticmethod
    def has_timed_out_before(algorithm_name: str, **input_data) -> bool:
        return False

    def generate_header(self):
        return self.past_header

    def _load_past_results(self):
        if not self.settings.re_build_table:
            try:
                with open(f'{self.settings.test_name}_results.csv', 'r') as file:
                    csv_reader = csv.reader(file)
                    self.past_header = next(csv_reader)
                    for name, *results in csv_reader:
                        self.past_results[name] = results
            except FileNotFoundError:
                self.settings.re_build_table = True

    def _merge_past_results(self):
        if not self.settings.re_build_table:
            for algorithm_name in self.algorithms:
                if algorithm_name not in self.past_results:
                    self.past_results[algorithm_name] = []

                if len(self.past_results[algorithm_name]) >= self.settings.max_depth:
                    self.results[algorithm_name] = self.past_results[algorithm_name]
                else:
                    self.results[algorithm_name] = [0 for _ in range(self.settings.max_depth)]
                    for i, past_result in enumerate(self.past_results[algorithm_name]):
                        try:
                            past_result = float(past_result)
                        except ValueError:
                            pass
                        self.results[algorithm_name][i] = past_result
        else:
            self.results = {algorithm_name: [0 for _ in range(self.settings.max_depth)] for algorithm_name in self.algorithms}

    def _is_timing_required(self, algorithm_name):
        return self.settings.re_build_table or self.is_timing_required(algorithm_name)

    def _save_data(self):  # TODO: fix saving location
        saved = False
        while not saved:
            try:
                with open(path.join(*self.settings.save_location, f'{self.settings.test_name}_results.csv'), 'w', newline='') as file:
                    csv_writer = csv.writer(file)

                    csv_writer.writerow(self.generate_header())

                    for name, data in self.results.items():
                        csv_writer.writerow([name, *data])
                saved = True
            except PermissionError:
                input('Permission Denied PRESS ENTER TO TRY AGAIN')


if __name__ == '__main__':
    main()
