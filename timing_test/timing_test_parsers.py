from timing_test.timer import Timer, TimerSettings
from timing_test.print_out import PrintOut
import os
from implementations import my_cyk_memo, my_cyk_numpy, my_cyk_memo_numpy, my_ll, my_cyk
from cfg import CFG
from typing import Dict, Callable, Any, Union
from tools import read_gram_file, convert_to_cnf, convert_cnf_to_list, words_of_length
import logging
import random

# Global test settings
MAX_DEPTH: int = 30
NUMBER_OF_CFGS_TO_TEST: int = 3
RE_RUNS: int = 3
USE_PAST_RESULTS: bool = True

TIMEOUT: int = 60
MAX_WORDS = 100


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
    general_cyk(cfg, max_depth, my_cyk_memo.parse, True)


def cyk_memo_numpy(cfg: CFG, max_depth: int):
    general_cyk(cfg, max_depth, my_cyk_memo_numpy.parse, True)


def cyk_numpy(cfg: CFG, max_depth: int):
    general_cyk(cfg, max_depth, my_cyk_numpy.parse, False)


def cyk(cfg: CFG, max_depth: int):
    cnf = convert_to_cnf(cfg)
    total = 0
    while total < MAX_WORDS:
        i = 0
        for i, word in enumerate(words_of_length(max_depth, cnf.alphabet)):
            if i > MAX_WORDS:
                return
            my_cyk.parse(word, cnf)
        total += i


def general_cyk(cfg: CFG, max_depth: int, parser, mem):
    cnf = convert_to_cnf(cfg)
    memo = {}
    rule_set = convert_cnf_to_list(cnf)
    total = 0
    while total < MAX_WORDS:
        i = 0
        for i, word in enumerate(words_of_length(max_depth, cnf.alphabet)):
            if i > MAX_WORDS:
                return
            if mem:
                parser(word, rule_set, memo)
            else:
                parser(word, rule_set)
        memo = {}
        total += i


def ll(cfg: CFG, max_depth: int):
    data = my_ll.generate_pre_calculated_data(cfg)
    total = 0
    while total < MAX_WORDS:
        i = 0
        for i, word in enumerate(words_of_length(max_depth, cfg.alphabet)):
            if i > MAX_WORDS:
                return
            my_ll.parse(word, cfg, data)
        total += i


class TimeAll(Timer):
    def __init__(self, *args, **kwargs):
        os.chdir(os.path.join('..', 'benchmarks'))
        global NUMBER_OF_CFGS_TO_TEST
        if NUMBER_OF_CFGS_TO_TEST != 0:
            rnd = random.Random(42)
            gram_files = rnd.sample(list(filter(lambda f: '.gram' == f[-5:], os.listdir())), NUMBER_OF_CFGS_TO_TEST)
            print(gram_files)
        else:
            gram_files = list(filter(lambda f: '.gram' == f[-5:], os.listdir()))
            NUMBER_OF_CFGS_TO_TEST = 'all'
        algorithms: Dict[str, Callable] = {
            'my_cyk_memo': cyk_memo,
            'my_cyk_numpy': cyk_numpy,
            'my_cyk_memo_numpy': cyk_memo_numpy,
            'my_cyk': cyk,
            # 'my_ll(NOT correct should be LL grammar)': ll,
        }

        super().__init__(TimerSettings(F'parsers_{NUMBER_OF_CFGS_TO_TEST}', save_location=('..', 'timing_test', 'results'),
                                       use_past_results=USE_PAST_RESULTS, re_runs=RE_RUNS, timeout=TIMEOUT, max_depth=MAX_DEPTH),
                         gram_files,
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
            self.results[algorithm_name][input_data['depth'] - 1] += result / MAX_WORDS

    def aggregate_results(self, algorithm_name: str, **input_data):
        self.results[algorithm_name][input_data['depth'] - 1] = round(
            self.results[algorithm_name][input_data['depth'] - 1] / (self.settings.re_runs * len(self.tests)), 3)

    def has_timed_out_before(self, algorithm_name: str, **input_data) -> bool:
        if self.results[algorithm_name][input_data['depth'] - 1] == self.settings.timeout_key:
            return True
        if input_data['depth'] - 2 >= 0 and self.results[algorithm_name][input_data['depth'] - 2] == self.settings.timeout_key:
            return True
        return False


if __name__ == '__main__':
    logging.basicConfig(filename='main.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    main()
