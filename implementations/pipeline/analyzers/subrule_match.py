from typing import List, Optional
import numpy as np

from cfg import cfg_rhs, CFG

from implementations.pipeline.pipeline_tools import PipelineDataManager, PipelineMethodData


class UnknownValueError(Exception):
    pass


def match_subrules(a: CFG, b: CFG, max_depth: int, pipeline: PipelineDataManager) -> Optional[bool]:
    list_rules_a, list_rules_b = pipeline.list_rules
    pipeline.data[method.key_word] = generate_similarity_table_by_value_approach(list_rules_a, list_rules_b)
    return None


def complexity_of_match_subrules(a: CFG, b: CFG, max_depth: int) -> int:
    return len(a.rules) * len(b.rules) * 3 * 12  # arbitrary for now


method = PipelineMethodData(
    match_subrules,
    complexity_of_match_subrules,
    'sub-rules'
)


def generate_similarity_table_by_value_approach(a, b):
    """
    Approach solution by continuously re calculating the similarity table starting with everything at 0
    """
    table = np.zeros([len(a), len(b)], dtype=np.float16)
    for _ in range(3):  # TODO: change this to check for how much the change happened
        for rule_a_index in range(1, len(a)):
            for rule_b_index in range(1, len(b)):
                rhs_a = a[rule_a_index]
                rhs_b = b[rule_b_index]
                table[rule_a_index, rule_b_index] = get_match_score(table, rhs_a, rhs_b, False)

    table[0, 0] = get_match_score(table, a[0], b[0], True)

    return table


def get_match_score(table, rule_a: cfg_rhs, rule_b: cfg_rhs, cheat: bool) -> float:
    if len(rule_a) > len(rule_b):
        return get_match_score_ls(table, rule_a, rule_b, cheat)
    return get_match_score_ls(table, rule_b, rule_a, cheat)


def get_match_score_ls(table, larger_rule, smaller_rule, cheat):
    matches: List[float] = [0 for _ in larger_rule]

    for index, rhs_rule_a in enumerate(larger_rule):
        for rhs_rule_b in smaller_rule:
            match = get_rhs_rule_match_score(table, rhs_rule_a, rhs_rule_b, cheat)
            matches[index] = max(match, matches[index])

    return sum(matches) / len(matches)


def get_rhs_rule_match_score(table, rule_a, rule_b, cheat) -> float:
    if type(rule_a) == type(rule_b):
        if type(rule_a) is tuple:
            left = table[rule_a[0], rule_b[0]]
            right = table[rule_a[1], rule_b[1]]
            if not cheat and (left < 0 or right < 0):
                raise UnknownValueError
            left, right = abs(left), abs(right)  # TODO: this assumes it is -1 if not defined
            return left * right
        else:
            if rule_a == rule_b:
                return 1
    return 0
