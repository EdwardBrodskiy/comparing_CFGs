from typing import Tuple
import numpy as np
from cfg import CFG
from implementations.pipeline.pipeline_tools import PipelineDataManager, PipelineMethodData
from implementations.pipeline.analyzers.subrule_match_optimized import get_reverse_reference, generate_iteration_order


def match_rhs_lengths(a: CFG, b: CFG, max_depth: int, pipeline: PipelineDataManager) -> Tuple[bool, float]:
    list_rules_a, list_rules_b = pipeline.list_rules

    table = np.zeros([len(list_rules_a), len(list_rules_b)], dtype=np.float16)

    # find reverse referencing
    reverse_reference_a = get_reverse_reference(list_rules_a)
    reverse_reference_b = get_reverse_reference(list_rules_b)

    # derive iteration order sets
    iteration_order_a = generate_iteration_order(reverse_reference_a)
    iteration_order_b = generate_iteration_order(reverse_reference_b)

    for iteration_a in iteration_order_a:
        for iteration_b in iteration_order_b:
            for rule_a_index in iteration_a:
                for rule_b_index in iteration_b:
                    rhs_a = list_rules_a[rule_a_index]
                    rhs_b = list_rules_b[rule_b_index]

                    try:
                        match = min(len(rhs_a), len(rhs_b)) / max(len(rhs_a), len(rhs_b))
                    except ZeroDivisionError:
                        match = 1
                    table[rule_a_index, rule_b_index] = match

    pipeline.tables[method.key_word] = table

    try:
        np.savetxt(r"comparisons\rhs_lengths.csv", table, delimiter=",")
    except FileNotFoundError:
        np.savetxt(r"rhs_lengths.csv", table, delimiter=",")
    return True, 0


def complexity_of_match_rhs_lengths(a: CFG, b: CFG, max_depth: int) -> int:
    return len(a.rules) * len(b.rules)


method = PipelineMethodData(
    match_rhs_lengths,
    complexity_of_match_rhs_lengths,
    'rhs_lengths'
)
