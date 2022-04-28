from timing_test.timer import Timer, TimerSettings
from timing_test.cfg_timer import CFGTimer
from timing_test.print_out import PrintOut
import os
from implementations import lark_testing, my_cyk_memo, my_cyk_numpy, my_cyk, my_cyk_memo_numpy, nltk_testing, sequencing as seq
from cfg import cnf_10palindrome
from typing import Dict, Callable

# Global test settings
MAX_DEPTH: int = 30
RE_RUNS: int = 5
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


def cyk(max_depth: int):
    return my_cyk.is_matching_cfg(cnf_10palindrome, cnf_10palindrome, max_depth=max_depth)


def cyk_numpy(max_depth: int):
    return my_cyk_numpy.is_matching_cfg(cnf_10palindrome, cnf_10palindrome, max_depth=max_depth)


def cyk_memo_numpy(max_depth: int):
    return my_cyk_memo_numpy.is_matching_cfg(cnf_10palindrome, cnf_10palindrome, max_depth=max_depth)


def cyk_memo(max_depth: int):
    return my_cyk_memo.is_matching_cfg(cnf_10palindrome, cnf_10palindrome, max_depth=max_depth)


def sequencing(max_depth: int):
    return seq.is_matching_cfg(cnf_10palindrome, cnf_10palindrome, max_depth=max_depth)


class TimePalindrome(CFGTimer):
    def __init__(self, *args, **kwargs):
        os.chdir(os.path.join('..', 'benchmarks'))

        algorithms: Dict[str, Callable[[int], bool]] = {
            'nltk_recursive_descent': nltk_testing.is_matching_cfg_wrapper_recursive_decent,
            'lark_earley': lark_testing.is_matching_cfg_wrapper_10palindrome_earley,
            'lark_cyk': lark_testing.is_matching_cfg_wrapper_10palindrome_cyk,
            'my_cyk': cyk,
            'my_cyk_numpy': cyk_numpy,
            'my_cyk_memo_numpy': cyk_memo_numpy,
            'my_cyk_memo': cyk_memo,
            'sequencing': sequencing,
        }

        super().__init__(TimerSettings('palindrome_test', save_location=('..', 'timing_test', 'results'),
                                       use_past_results=USE_PAST_RESULTS, re_runs=RE_RUNS, timeout=TIMEOUT, max_depth=MAX_DEPTH),
                         ['palindrome'],
                         algorithms, *args, **kwargs)

    @staticmethod  # TODO: may be able to expand out the cnf and depth variables
    def algorithm_wrapper(algorithm: Callable[[int], bool], **kwargs) -> Callable[[], bool]:
        return lambda: algorithm(kwargs['depth'])


if __name__ == '__main__':
    main()
