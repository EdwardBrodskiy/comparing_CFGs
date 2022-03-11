from timing_test.timer import Timer, TimerSettings
from timing_test.print_out import PrintOut
import os
from implementations import my_cfg_analyzer, my_cyk_memo, my_cyk_numpy, my_cyk
import implementations.agc.main as agc_enum
from implementations.pipeline import pipeline_analyzer
from cfg import type_is_matching_cfg, cnf_10palindrome
from typing import Dict, Callable, Union, Any

# Global test settings
MAX_DEPTH: int = 12
RE_RUNS: int = 3
USE_PAST_RESULTS: bool = False


def main():
    import cProfile
    import pstats
    with cProfile.Profile() as pr:
        timing_test_time_all = TimePalindrome(
            printer=PrintOut(key={'|': 'completed a test cycle', '-': 'completed all tests of a given test case',
                                  '.': 'completed a depth for all algorithms'}))
        timing_test_time_all.run()
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()
    stats.dump_stats(filename='timing_test_all_PROFILE.prof')


class TimePalindrome(Timer):
    def __init__(self, *args, **kwargs):
        os.chdir(os.path.join('..', 'benchmarks'))

        algorithms: Dict[str, type_is_matching_cfg] = {
            'my_cyk': my_cyk.is_matching_cfg,
            'my_cyk_numpy': my_cyk_numpy.is_matching_cfg,
            'my_cyk_memo': my_cyk_memo.is_matching_cfg,
            'agc_enum': agc_enum.is_matching_cfg_depth_respecting,
            'agc_enum_memo': agc_enum.is_matching_cfg_depth_respecting_memo,
            # 'my_cfg_analyzer': my_cfg_analyzer.is_matching_cfg,
            # 'pipeline_analyzer': pipeline_analyzer.is_matching_cfg
        }

        super().__init__(TimerSettings('palindrome_test', save_location=('..', 'timing_test', 'results'),
                                       re_build_table=USE_PAST_RESULTS, re_runs=RE_RUNS), ['palindrome'],
                         algorithms, *args, **kwargs)

    @staticmethod
    def set_up(test: str) -> Dict[str, Any]:
        return {
            'cnf': cnf_10palindrome,
        }

    @staticmethod
    def generate_varying_input_data_for_test():
        for i in range(1, MAX_DEPTH + 1):
            yield i, {'depth': i}

    @staticmethod  # TODO: may be able to expand out the cnf and depth variables
    def algorithm_wrapper(algorithm: type_is_matching_cfg, **kwargs) -> Callable[[], bool]:
        return lambda: algorithm(kwargs['cnf'], kwargs['cnf'], kwargs['depth'])

    def add_result_to_results(self, run_index: int, algorithm_name: str, result: Union[str, float], **input_data):
        self.results[algorithm_name][input_data['depth'] - 1] += result
        if run_index + 1 == self.settings.re_runs:  # turn sum to mean at the last result
            self.results[algorithm_name][input_data['depth'] - 1] = round(
                self.results[algorithm_name][input_data['depth'] - 1] / (self.settings.re_runs * len(self.tests)), 3)


if __name__ == '__main__':
    main()
