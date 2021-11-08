from typing import List, Callable, Dict, Any, Optional

import numpy as np
import heapq

from cfg import convert_cnf_to_list, CFG, cnf_10palindrome
from implementations.my_cyk_numpy import parse

from implementations.my_cyk_numpy import is_matching_cfg as numpy_is_matching_cfg

pipeline_data = Dict[str, Any]

pipeline_function = Callable[[CFG, CFG, int, pipeline_data], Optional[bool]]


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
                                     [
                                         is_matching_alphabet,
                                         lambda *args: numpy_is_matching_cfg(*args[:-1])
                                     ])


def is_matching_cfg_pipelined(a: CFG, b: CFG, max_depth: int, pipeline: List[pipeline_function]):
    data: pipeline_data = {}
    for pipe in pipeline:
        decision = pipe(a, b, max_depth, data)
        if decision is not None:
            return decision
    return True


def is_matching_alphabet(a: CFG, b: CFG, max_depth: int, pipeline) -> Optional[bool]:
    if a.alphabet != b.alphabet:
        return False
    return None


if __name__ == '__main__':
    main()
