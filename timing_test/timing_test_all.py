from timing_test.timer import TimerSettings
from timing_test.cfg_timer import CFGTimer
from timing_test.print_out import PrintOut
import os
from implementations import my_cfg_analyzer, my_cyk_memo, my_cyk_memo_numpy
from implementations.pipeline import pipeline_analyzer
from implementations.agc import main as agc
from implementations.agc import multi as agc_multi
from cfg import type_is_matching_cfg, CFG
from typing import Dict, Callable, Union, Any
from tools import read_gram_file, convert_to_cnf
import logging
import time

# Global test settings
MAX_DEPTH: int = 30
NUMBER_OF_CFGS_TO_TEST: int = 1
RE_RUNS: int = 1
USE_PAST_RESULTS: bool = False
TIMEOUT: int = 120


def main():
    import cProfile
    import pstats
    with cProfile.Profile() as pr:
        timing_test_time_all = TimeAll(
            printer=PrintOut(key={'|': 'completed a test cycle', '-': 'completed all tests of a given test case',
                                  '.': 'completed a depth for all algorithms'}))
        timing_test_time_all.run()
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()
    stats.dump_stats(filename='timing_test_all_PROFILE.prof')


def multiprocessing_is_matching_cfg(a: CFG, b: CFG, max_depth: int):
    try:
        return agc_multi.is_matching_cfg(a, b, max_depth, timeout=TIMEOUT, is_main=lambda: __name__ == '__main__')
    except TimeoutError:
        time.sleep(1)
        return True


class TimeAll(CFGTimer):
    def __init__(self, *args, **kwargs):
        os.chdir(os.path.join('..', 'benchmarks'))
        global NUMBER_OF_CFGS_TO_TEST
        if NUMBER_OF_CFGS_TO_TEST != 0:
            gram_files = list(filter(lambda f: '.gram' == f[-5:], os.listdir()))[:NUMBER_OF_CFGS_TO_TEST]
        else:
            gram_files = list(filter(lambda f: '.gram' == f[-5:], os.listdir()))
            NUMBER_OF_CFGS_TO_TEST = 'all'
        algorithms: Dict[str, type_is_matching_cfg] = {
            # 'my_cyk_memo': my_cyk_memo.is_matching_cfg,
            # 'my_cyk_memo_numpy': my_cyk_memo_numpy.is_matching_cfg,
            # 'my_cfg_analyzer': my_cfg_analyzer.is_matching_cfg,
            # 'pipeline_analyzer': pipeline_analyzer.is_matching_cfg,
            'agc': agc.is_matching_cfg,
            # 'agc_enum_multiprocessing': multiprocessing_is_matching_cfg,
        }

        super().__init__(TimerSettings(F'time_equal_{NUMBER_OF_CFGS_TO_TEST}', save_location=('..', 'timing_test', 'results'),
                                       use_past_results=USE_PAST_RESULTS, re_runs=RE_RUNS, timeout=TIMEOUT, max_depth=MAX_DEPTH),
                         gram_files,
                         algorithms, *args, **kwargs)

    @staticmethod
    def set_up(test: str) -> Dict[str, Any]:
        cfg = read_gram_file(test)
        cnf = convert_to_cnf(cfg)
        return {
            'cnf': cnf,
        }

    @staticmethod  # TODO: may be able to expand out the cnf and depth variables
    def algorithm_wrapper(algorithm: type_is_matching_cfg, **kwargs) -> Callable[[], bool]:
        return lambda: algorithm(kwargs['cnf'], kwargs['cnf'], kwargs['depth'])


if __name__ == '__main__':
    logging.basicConfig(filename='main.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    main()
