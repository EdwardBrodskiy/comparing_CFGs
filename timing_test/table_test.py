from timing_test.timer import Timer, TimerSettings
from typing import Union, Dict, Any, Callable
import os
import pandas as pd
import numpy as np

from tools import read_gram_file, convert_to_cnf
from cfg import type_is_matching_cfg
from timing_test.print_out import PrintOut

from implementations.pipeline import pipeline_analyzer
from implementations.agc import main as agc

import random
import time

# Global test settings
NUMBER_OF_LANGUAGES_TO_TEST: int = 5
TIMEOUT: int = 60
ERROR_TYPE: int = 2


def main():
    timing_test_time_all = TableTimer(
        printer=PrintOut(key={'|': 'completed a test cycle', '-': 'completed all tests of a given grammar',
                              '.': 'completed a modified grammar for all algorithms'}))
    timing_test_time_all.run()


class TableTimer(Timer):

    def __init__(self, *args, **kwargs):
        os.chdir(os.path.join('..', 'benchmarks'))

        gram_files = filter(lambda f: '.gram' == f[-5:], os.listdir())
        gram_files = map(lambda f: f[:-5], gram_files)
        tests = list(filter(lambda f: '-' not in f, gram_files))
        self.row_values = tests
        algorithms: Dict[str, type_is_matching_cfg] = {
            # 'pipeline_analyzer': pipeline_analyzer.is_matching_cfg,
            # 'agc_implementation_depth_respecting': agc.is_matching_cfg_depth_respecting,
            'agc_depth_respecting_memo': agc.is_matching_cfg_depth_respecting_memo,
        }

        super().__init__(
            TimerSettings(F'table_err_{ERROR_TYPE}_timeout_{TIMEOUT}', save_location=('..', 'timing_test'),
                          use_past_results=False, re_runs=1, max_depth=30, timeout=TIMEOUT), tests,
            algorithms, *args, **kwargs)

    def generate_varying_input_data_for_test(self):
        for i in range(10):
            yield i, {'grammar_index': i}

    @staticmethod
    def set_up(test: str) -> Dict[str, Any]:
        original = convert_to_cnf(read_gram_file(test + '.gram'))
        modified = [convert_to_cnf(read_gram_file(f'{test}-{ERROR_TYPE}-{i}.gram')) for i in range(1, 11)]
        return {
            'name': test,
            'original': original,
            'modified': modified
        }

    def algorithm_wrapper(self, algorithm: type_is_matching_cfg, **kwargs) -> Callable[[], bool]:
        return lambda: algorithm(kwargs['original'], kwargs['modified'][kwargs['grammar_index']], self.settings.max_depth)

    def add_result_to_results(self, run_index: int, algorithm_name: str, result: Union[str, float], **input_data):
        if result == self.settings.timeout_key:
            pass
        else:
            self.results.loc[self.results['grammar'] == input_data['name'], f'{algorithm_name}-time'] += result
            self.results.loc[self.results['grammar'] == input_data['name'], f'{algorithm_name}-disproved'] += 1

    def has_timed_out_before(self, algorithm_name: str, **input_data) -> bool:
        return False

    def _load_past_results(self):
        pass

    def _merge_past_results(self):
        data = {
            'grammar': self.row_values,
        }
        algorithm_columns = []
        for algorithm in self.algorithms:
            algorithm_columns.append(f'{algorithm}-disproved')
            algorithm_columns.append(f'{algorithm}-time')

        for algorithm_column in algorithm_columns:
            data[algorithm_column] = [0 for _ in self.row_values]

        self.results = pd.DataFrame(data=data, columns=['grammar', *algorithm_columns])

        with open(os.path.join(*self.settings.save_location, f'{self.settings.test_name}_results.csv'), 'w', newline='') as file:
            file.write(self.results.to_csv(index=False))

    def _save_data(self):
        saved = False
        for algorithm in self.algorithms:
            self.results[f'{algorithm}-time'] /= self.results[f'{algorithm}-disproved']
        pd.set_option('display.max_columns', 20)
        print('\n   Results:\n', self.results)
        while not saved:
            try:
                with open(os.path.join(*self.settings.save_location, f'{self.settings.test_name}_results.csv'), 'w', newline='') as file:
                    file.write(self.results.to_csv(index=False))
                saved = True
            except PermissionError:
                input('Permission Denied PRESS ENTER TO TRY AGAIN')


if __name__ == '__main__':
    main()
