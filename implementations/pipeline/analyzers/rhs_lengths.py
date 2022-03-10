from typing import Tuple
import numpy as np
from cfg import CFG
from implementations.pipeline.pipeline_tools import PipelineDataManager, PipelineMethodData


def match_rhs_lengths(a: CFG, b: CFG, max_depth: int, pipeline: PipelineDataManager) -> Tuple[bool, float]:
    list_rules_a, list_rules_b = pipeline.list_rules

    table = np.zeros([len(list_rules_a), len(list_rules_b)], dtype=np.float16)

    for rule_a_index, rhs_a in enumerate(list_rules_a):
        for rule_b_index, rhs_b in enumerate(list_rules_b):
            match = min(len(rhs_a), len(rhs_b)) / max(len(rhs_a), len(rhs_b))
            table[rule_a_index, rule_b_index] = match

    pipeline.tables[method.key_word] = table
    np.savetxt("rhs_lengths.csv", table, delimiter=",")
    return True, 0


def complexity_of_match_rhs_lengths(a: CFG, b: CFG, max_depth: int) -> int:
    return len(a.rules) * len(b.rules)


method = PipelineMethodData(
    match_rhs_lengths,
    complexity_of_match_rhs_lengths,
    'rhs_lengths'
)
