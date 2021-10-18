from timing_test.timer import Timer, TimerSettings
import os
from implementations import my_cfg_analyzer, my_cyk_memo, my_cyk_numpy
from cfg import type_is_matching_cfg
from typing import Dict, Callable, Union, Any
from tools import read_gram_file, convert_to_cnf


def main():
    timing_test_time_all = TimeAll()
    timing_test_time_all.run()


class TimeAll(Timer):
    def __init__(self):
        os.chdir(os.path.join('..', 'benchmarks'))
        gram_files = list(filter(lambda f: '.gram' == f[-5:], os.listdir()))

        algorithms: Dict[str, type_is_matching_cfg] = {
            'my_cyk_numpy': my_cyk_numpy.is_matching_cfg,
            'my_cyk_memo': my_cyk_memo.is_matching_cfg,
            # 'my_cfg_analyzer': my_cfg_analyzer.is_matching_cfg
        }
        super().__init__(TimerSettings('time_all', save_location=('..', 'timing_test', 'results')), gram_files, algorithms)

    @staticmethod
    def set_up(test: str) -> Dict[str, Any]:
        start, cfg = read_gram_file(test)
        start, cnf, alphabet = convert_to_cnf(start, cfg)
        return {
            'start': start,
            'cnf': cnf,
            'alphabet': alphabet
        }

    @staticmethod  # TODO: may be able to expand out the cnf and depth variables
    def algorithm_wrapper(algorithm: type_is_matching_cfg, **kwargs) -> Callable[[], bool]:
        return lambda: algorithm(kwargs['cnf'], kwargs['cnf'], kwargs['alphabet'], kwargs['depth'])

    def add_result_to_results(self, run_index: int, algorithm_name: str, result: Union[str, float], **input_data):
        self.results[algorithm_name][input_data['depth'] - 1] += result
        if run_index + 1 == self.settings.re_runs:
            self.results[algorithm_name][input_data['depth'] - 1] = round(
                self.results[algorithm_name][input_data['depth'] - 1] / self.settings.re_runs, 3)


if __name__ == '__main__':
    main()