from typing import Tuple

from cfg import cnf_10palindrome
from implementations.my_cyk_numpy import is_matching_cfg as numpy_is_matching_cfg
from implementations.pipeline.pipeline import pipeline_function
from implementations.pipeline.analyzers import *
from implementations.pipeline.comparators import *


def main():
    import cProfile
    import pstats
    from tools import convert_to_cnf, read_gram_file
    start, cfg = read_gram_file(r'..\benchmarks\C11Grammar1-1-1.gram')
    cnf = convert_to_cnf(start, cfg)
    with cProfile.Profile() as pr:
        is_matching_cfg(cnf, cnf, 1)
    stats = pstats.Stats(pr)
    stats.dump_stats(filename='pipeline.prof')


def is_matching_cfg(a: CFG, b: CFG, max_depth: int):
    return is_matching_cfg_pipelined(a, b, max_depth,
                                     (
                                         is_matching_alphabet,
                                         match_rhs_lengths,
                                         lambda *args: numpy_is_matching_cfg(*args[:-1])
                                     ))


def is_matching_cfg_pipelined(a: CFG, b: CFG, max_depth: int, pipeline: Tuple[pipeline_function, ...]):
    data = Pipeline(a, b, max_depth)
    for pipe in pipeline:
        decision = pipe(a, b, max_depth, data)
        if decision is not None:
            return decision
    return True


if __name__ == '__main__':
    main()
