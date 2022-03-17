from timing_test.timer import Timer, TimerSettings
from timing_test.print_out import PrintOut
import os
from implementations import my_cfg_analyzer, my_cyk_memo, my_cyk_numpy, my_cyk_memo_numpy
from implementations.pipeline import pipeline_analyzer
from implementations.agc import main as agc
from cfg import type_is_matching_cfg, CFG
from typing import Dict, Callable, Any, Union
from tools import read_gram_file, convert_to_cnf, convert_cnf_to_list, words_of_length

# Global test settings
MAX_DEPTH: int = 30
NUMBER_OF_CFGS_TO_TEST: int = 2
RE_RUNS: int = 1
USE_PAST_RESULTS: bool = True
TIMEOUT: int = 300


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


wrapped_parser = Callable[[CFG, int], bool]


def cyk_memo(cfg: CFG, max_depth: int):
    cnf = convert_to_cnf(cfg)
    memo = {}
    rule_set = convert_cnf_to_list(cnf)

    for word in words_of_length(max_depth, cnf.alphabet):
        my_cyk_memo.parse(word, rule_set, memo)


class TimeAll(Timer):
    def __init__(self, *args, **kwargs):
        os.chdir(os.path.join('..', 'benchmarks'))
        global NUMBER_OF_CFGS_TO_TEST
        if NUMBER_OF_CFGS_TO_TEST != 0:
            gram_files = list(filter(lambda f: '.gram' == f[-5:], os.listdir()))[:NUMBER_OF_CFGS_TO_TEST]
        else:
            gram_files = list(filter(lambda f: '.gram' == f[-5:], os.listdir()))
            NUMBER_OF_CFGS_TO_TEST = 'all'
        algorithms: Dict[str, Callable] = {
            'my_cyk_memo': cyk_memo,
            # 'my_cyk_numpy': my_cyk_numpy.is_matching_cfg,

            # 'my_cyk_memo_numpy': my_cyk_memo_numpy.is_matching_cfg,
            # 'my_cfg_analyzer': my_cfg_analyzer.is_matching_cfg,
            # 'pipeline_analyzer': pipeline_analyzer.is_matching_cfg,
            # 'agc_implementation_random': agc.is_matching_cfg,
            # 'agc_implementation_depth_respecting': agc.is_matching_cfg_depth_respecting,
            # 'agc_implementation_depth_respecting_memo': agc.is_matching_cfg_depth_respecting_memo,
        }

        super().__init__(TimerSettings(F'parsers_{NUMBER_OF_CFGS_TO_TEST}', save_location=('..', 'timing_test', 'results'),
                                       re_build_table=USE_PAST_RESULTS, re_runs=RE_RUNS, timeout=TIMEOUT, max_depth=MAX_DEPTH), gram_files,
                         algorithms, *args, **kwargs)

    @staticmethod
    def set_up(test: str) -> Dict[str, Any]:
        cfg = read_gram_file(test)
        return {
            'cfg': cfg,
        }

    @staticmethod  # TODO: may be able to expand out the cnf and depth variables
    def algorithm_wrapper(algorithm: wrapped_parser, **kwargs) -> Callable[[], bool]:
        return lambda: algorithm(kwargs['cfg'], kwargs['depth'])

    def generate_varying_input_data_for_test(self):
        for i in range(1, self.settings.max_depth + 1):
            yield i, {'depth': i}

    def add_result_to_results(self, run_index: int, algorithm_name: str, result: Union[str, float], **input_data):
        if result == self.settings.timeout_key or self.results[algorithm_name][input_data['depth'] - 1] == self.settings.timeout_key:
            self.results[algorithm_name][input_data['depth'] - 1] = self.settings.timeout_key
        else:

            self.results[algorithm_name][input_data['depth'] - 1] += result

    def aggregate_results(self, algorithm_name: str, **input_data):
        number_of_words = len(list(words_of_length(input_data['depth'], input_data['cfg'].alphabet)))
        self.results[algorithm_name][input_data['depth'] - 1] = round(
            self.results[algorithm_name][input_data['depth'] - 1] / (self.settings.re_runs * len(self.tests) * number_of_words), 3)

    def has_timed_out_before(self, algorithm_name: str, **input_data) -> bool:
        if self.results[algorithm_name][input_data['depth'] - 1] == self.settings.timeout_key:
            return True
        if input_data['depth'] - 2 >= 0 and self.results[algorithm_name][input_data['depth'] - 2] == self.settings.timeout_key:
            return True
        return False


if __name__ == '__main__':
    main()
