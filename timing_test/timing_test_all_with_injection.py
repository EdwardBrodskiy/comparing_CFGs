from timing_test.timer import Timer, TimerSettings
from timing_test.cfg_timer import CFGTimer
from timing_test.print_out import PrintOut
import os
from implementations import my_cfg_analyzer, my_cyk_memo, my_cyk_numpy
from implementations.pipeline import pipeline_analyzer
from implementations.agc import main as agc
from cfg import type_is_matching_cfg, CFG
from typing import Dict, Callable, Union, Any
from tools import read_gram_file, convert_to_cnf
from tests.implementations.tools_for_testing import inject_type_1_errors, inject_type_2_errors, inject_type_3_errors, get_alphabet
import logging

# Global test settings
MAX_DEPTH: int = 30
NUMBER_OF_CFGS_TO_TEST: int = 1
RE_RUNS: int = 1
USE_PAST_RESULTS: bool = False
TIMEOUT: int = 120
ERROR_TYPE: int = 2


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
            # 'my_cyk_numpy': my_cyk_numpy.is_matching_cfg,
            # 'my_cyk_memo': my_cyk_memo.is_matching_cfg,
            # 'my_cfg_analyzer': my_cfg_analyzer.is_matching_cfg,
            # 'pipeline_analyzer': pipeline_analyzer.is_matching_cfg,
            # 'agc_implementation_random': agc.is_matching_cfg,
            'agc_implementation_depth_respecting_memo': agc.is_matching_cfg,
        }

        super().__init__(
            TimerSettings(F'time_type_{ERROR_TYPE}_err_{NUMBER_OF_CFGS_TO_TEST}', save_location=('..', 'timing_test', 'results'),
                          use_past_results=USE_PAST_RESULTS, re_runs=RE_RUNS, max_depth=MAX_DEPTH, timeout=TIMEOUT), gram_files,
            algorithms, *args, **kwargs)

    @staticmethod
    def set_up(test: str) -> Dict[str, Any]:
        cfg = read_gram_file(test)
        cnf = convert_to_cnf(cfg)
        error_injectors = {
            1: lambda: next(inject_type_1_errors(cnf, sample_size=1, be_consistent=False)),
            2: lambda: convert_to_cnf(next(inject_type_2_errors(cfg, sample_size=1, be_consistent=False))),  # TODO : fix cnf
            # 3: lambda: convert_to_cnf(next(inject_type_2_errors(cfg, sample_size=1, be_consistent=False))),
        }
        return {
            'cnf': cnf,
            'bad_cnf': error_injectors[ERROR_TYPE]()
        }

    @staticmethod  # TODO: may be able to expand out the cnf and depth variables js style
    def algorithm_wrapper(algorithm: type_is_matching_cfg, **kwargs) -> Callable[[], bool]:
        return lambda: algorithm(kwargs['cnf'], kwargs['bad_cnf'], kwargs['depth'])


if __name__ == '__main__':
    logging.basicConfig(filename='main.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    main()
