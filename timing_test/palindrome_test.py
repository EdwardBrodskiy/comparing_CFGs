from timing_test.timer import Timer, TimerSettings
from timing_test.cfg_timer import CFGTimer
from timing_test.print_out import PrintOut
import os
from implementations import my_cfg_analyzer, my_cyk_memo, my_cyk_numpy, my_cyk, my_cyk_memo_numpy
import implementations.agc.main as agc_enum
from implementations.pipeline import pipeline_analyzer
from cfg import type_is_matching_cfg, cnf_10palindrome
from typing import Dict, Callable, Union, Any

# Global test settings
MAX_DEPTH: int = 30
RE_RUNS: int = 3
USE_PAST_RESULTS: bool = False
TIMEOUT: int = 60


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


class TimePalindrome(CFGTimer):
    def __init__(self, *args, **kwargs):
        os.chdir(os.path.join('..', 'benchmarks'))

        algorithms: Dict[str, type_is_matching_cfg] = {
            'my_cyk': my_cyk.is_matching_cfg,
            'my_cyk_numpy': my_cyk_numpy.is_matching_cfg,
            'my_cyk_memo_numpy': my_cyk_memo_numpy.is_matching_cfg,
            'my_cyk_memo': my_cyk_memo.is_matching_cfg,
            'agc_enum': agc_enum.is_matching_cfg_depth_respecting,
            'agc_enum_memo': agc_enum.is_matching_cfg_depth_respecting_memo,
            # 'my_cfg_analyzer': my_cfg_analyzer.is_matching_cfg,
            # 'pipeline_analyzer': pipeline_analyzer.is_matching_cfg
        }

        super().__init__(TimerSettings('palindrome_test', save_location=('..', 'timing_test', 'results'),
                                       re_build_table=USE_PAST_RESULTS, re_runs=RE_RUNS, timeout=TIMEOUT, max_depth=MAX_DEPTH),
                         ['palindrome'],
                         algorithms, *args, **kwargs)

    @staticmethod
    def set_up(test: str) -> Dict[str, Any]:
        return {
            'cnf': cnf_10palindrome,
        }

    @staticmethod  # TODO: may be able to expand out the cnf and depth variables
    def algorithm_wrapper(algorithm: type_is_matching_cfg, **kwargs) -> Callable[[], bool]:
        return lambda: algorithm(kwargs['cnf'], kwargs['cnf'], kwargs['depth'])


if __name__ == '__main__':
    main()
