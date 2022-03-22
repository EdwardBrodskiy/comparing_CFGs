from timing_test.timer import Timer, TimerSettings
from timing_test.print_out import PrintOut
import os
from implementations import my_cyk_memo, my_cyk_numpy, my_cyk_memo_numpy, my_ll, my_cyk, lark_testing
from cfg import CFG, cnf_10palindrome
from typing import Dict, Callable, Any, Union
from tools import read_gram_file, convert_to_cnf, convert_cnf_to_list, words_of_length, convert_broken_cnf_to_cfg_form
import logging
import math

# Global test settings
MAX_DEPTH: int = 30
RE_RUNS: int = 3
USE_PAST_RESULTS: bool = True

TIMEOUT: int = 60
MAX_WORDS = 1000


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


wrapped_parser = Callable[[int], None]


def cyk_memo(max_depth: int):
    general_cyk(max_depth, my_cyk_memo.parse, True)


def cyk_memo_numpy(max_depth: int):
    general_cyk(max_depth, my_cyk_memo_numpy.parse, True)


def cyk_numpy(max_depth: int):
    general_cyk(max_depth, my_cyk_numpy.parse, False)


def cyk(max_depth: int):
    cnf = cnf_10palindrome
    total = 0
    while total < MAX_WORDS:
        i = 0
        for i, word in enumerate(words_of_length(max_depth, cnf.alphabet)):
            if i > MAX_WORDS:
                return
            my_cyk.parse(word, cnf)
        total += i


def general_cyk(max_depth: int, parser, mem):
    cnf = cnf_10palindrome
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


def ll(max_depth: int):
    cfg = convert_broken_cnf_to_cfg_form(cnf_10palindrome)
    data = my_ll.generate_pre_calculated_data(cfg)
    total = 0
    while total < MAX_WORDS:
        i = 0
        for i, word in enumerate(words_of_length(max_depth, cfg.alphabet)):
            if i > MAX_WORDS:
                return
            my_ll.parse(word, cfg, data)
        total += i


def lark_earley(max_depth: int):
    lark(lark_testing.cfg_10palindrome, max_depth)


def lark_cyk(max_depth: int):
    lark(lark_testing.cnf_10palindrome, max_depth)


def lark(cfg, max_depth: int):
    total = 0
    alphabet = ['1', '0']
    while total < MAX_WORDS:
        i = 0
        for i, word in enumerate(words_of_length(max_depth, alphabet)):
            if i > MAX_WORDS:
                return
            word = ''.join(word)
            lark_testing.is_accepted(cfg, word)
        total += i


class TimeAll(Timer):
    def __init__(self, *args, **kwargs):
        os.chdir(os.path.join('..', 'benchmarks'))

        algorithms: Dict[str, Callable] = {
            'my_cyk_memo': cyk_memo,
            'my_cyk_numpy': cyk_numpy,
            'my_cyk_memo_numpy': cyk_memo_numpy,
            'my_cyk': cyk,
            'lark_earley': lark_earley,
            'lark_cyk': lark_cyk
        }

        super().__init__(TimerSettings(F'simple_parsers', save_location=('..', 'timing_test', 'results'),
                                       re_build_table=USE_PAST_RESULTS, re_runs=RE_RUNS, timeout=TIMEOUT, max_depth=MAX_DEPTH), ['10pali'],
                         algorithms, *args, **kwargs)

    @staticmethod
    def set_up(test: str) -> Dict[str, Any]:
        return {}

    @staticmethod  # TODO: may be able to expand out the cnf and depth variables
    def algorithm_wrapper(algorithm: wrapped_parser, **kwargs) -> Callable[[], bool]:
        return lambda: algorithm(kwargs['depth'])

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
