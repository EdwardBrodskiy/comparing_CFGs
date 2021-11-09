from typing import List, Callable, Dict, Any, Optional

import numpy as np
import heapq

from cfg import convert_cnf_to_list, CFG, cnf_10palindrome
from implementations.my_cyk_numpy import parse

from implementations.my_cyk_numpy import is_matching_cfg as numpy_is_matching_cfg


class Pipeline:
    def __init__(self, a: CFG, b: CFG, max_depth: int):
        self._a = a
        self._b = b
        self.max_depth = max_depth

        self._list_rules = None

        self.data: Dict[str, np.ndarray] = {}

    @property
    def list_rules(self):
        if self._list_rules is not None:
            return self._list_rules
        self._list_rules = convert_cnf_to_list(self._a), convert_cnf_to_list(self._b)
        return self._list_rules


'''
INPUT: 2 CFGs that are to be compared a maximum depth and work of prior pipes
RETURN: Give back True or False if analysis was decisive otherwise return None 
'''
pipeline_function = Callable[[CFG, CFG, int, Pipeline], Optional[bool]]


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
                                         match_rhs_lengths,
                                         lambda *args: numpy_is_matching_cfg(*args[:-1])
                                     ])


def is_matching_cfg_pipelined(a: CFG, b: CFG, max_depth: int, pipeline: List[pipeline_function]):
    data = Pipeline(a, b, max_depth)
    for pipe in pipeline:
        decision = pipe(a, b, max_depth, data)
        if decision is not None:
            return decision
    return True


def is_matching_alphabet(a: CFG, b: CFG, max_depth: int, pipeline: Pipeline) -> Optional[bool]:
    if a.alphabet != b.alphabet:
        return False
    return None


def match_rhs_lengths(a: CFG, b: CFG, max_depth: int, pipeline: Pipeline) -> Optional[bool]:
    list_rules_a, list_rules_b = pipeline.list_rules

    table = np.zeros([len(list_rules_a), len(list_rules_b)], dtype=np.float16)

    for rule_a_index, rhs_a in enumerate(list_rules_a):
        for rule_b_index, rhs_b in enumerate(list_rules_b):
            match = min(len(rhs_a), len(rhs_b)) / max(len(rhs_a), len(rhs_b))
            table[rule_a_index, rule_b_index] = match

    pipeline.data['rhs_lengths'] = table
    return None


if __name__ == '__main__':
    main()
