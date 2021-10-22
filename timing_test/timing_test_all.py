from timing_test.timer import Timer, TimerSettings
from timing_test.print_out import PrintOut
import os
from implementations import my_cfg_analyzer, my_cyk_memo, my_cyk_numpy
from cfg import type_is_matching_cfg
from typing import Dict, Callable, Union, Any
from tools import read_gram_file, convert_to_cnf

# Global test settings
MAX_DEPTH = 2
NUMBER_OF_CFGS_TO_TEST = 3
USE_PAST_RESULTS = False


def main():
    timing_test_time_all = TimeAll(
        printer=PrintOut(key={'|': 'completed a test cycle', '-': 'completed all tests of a given test case',
                              '.': 'completed a depth for all algorithms'}))
    timing_test_time_all.run()


class TimeAll(Timer):
    def __init__(self, *args, **kwargs):
        os.chdir(os.path.join('..', 'benchmarks'))
        global NUMBER_OF_CFGS_TO_TEST
        if NUMBER_OF_CFGS_TO_TEST != 0:
            gram_files = list(filter(lambda f: '.gram' == f[-5:], os.listdir()))[:NUMBER_OF_CFGS_TO_TEST]
        else:
            gram_files = list(filter(lambda f: '.gram' == f[-5:], os.listdir()))
            NUMBER_OF_CFGS_TO_TEST = 'all'
        algorithms: Dict[str, type_is_matching_cfg] = {
            # 'my_cyk_numpy': my_cyk_numpy.is_matching_cfg,
            'my_cyk_memo': my_cyk_memo.is_matching_cfg,
            # 'my_cfg_analyzer': my_cfg_analyzer.is_matching_cfg
        }

        super().__init__(TimerSettings(F'time_{NUMBER_OF_CFGS_TO_TEST}', save_location=('..', 'timing_test', 'results'),
                                       re_build_table=USE_PAST_RESULTS), gram_files,
                         algorithms, *args, **kwargs)

    @staticmethod
    def set_up(test: str) -> Dict[str, Any]:
        start, cfg = read_gram_file(test)
        start, cnf, alphabet = convert_to_cnf(start, cfg)
        return {
            'start': start,
            'cnf': cnf,
            'alphabet': alphabet
        }

    @staticmethod
    def generate_varying_input_data_for_test():
        for i in range(1, MAX_DEPTH + 1):
            yield i, {'depth': i}

    @staticmethod  # TODO: may be able to expand out the cnf and depth variables
    def algorithm_wrapper(algorithm: type_is_matching_cfg, **kwargs) -> Callable[[], bool]:
        return lambda: algorithm(kwargs['cnf'], kwargs['start'], kwargs['cnf'], kwargs['start'], kwargs['alphabet'], kwargs['depth'])

    def add_result_to_results(self, run_index: int, algorithm_name: str, result: Union[str, float], **input_data):
        self.results[algorithm_name][input_data['depth'] - 1] += result
        if run_index + 1 == self.settings.re_runs:  # turn sum to mean at the last result
            self.results[algorithm_name][input_data['depth'] - 1] = round(
                self.results[algorithm_name][input_data['depth'] - 1] / (self.settings.re_runs * len(self.tests)), 3)


if __name__ == '__main__':
    main()
