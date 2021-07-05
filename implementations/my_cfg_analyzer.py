from cfg import cnf_10palindrome, alphabet10, convert_rules_to_list
import numpy as np
from typing import List


class UnknownValueError(Exception):
    pass


def is_matching_cfg(a, b, alphabet, max_depth: int):
    memo_a = {}
    memo_b = {}
    a = convert_rules_to_list(a)
    b = convert_rules_to_list(b)
    table = np.ones([len(a), len(b)], dtype=np.float16) * -1  # table of -1's

    for rule_a in range(1, len(a)):
        for rule_b in range(1, len(b)):
            if table[rule_a, rule_b] < 0:
                rhs_a = a[rule_a]
                rhs_b = b[rule_b]
                try:
                    if len(rhs_a) > len(rhs_b):
                        table[rule_a, rule_b] = get_match_score(table, rhs_a, rhs_b)
                    else:
                        table[rule_a, rule_b] = get_match_score(table, rhs_b, rhs_a)
                except UnknownValueError:
                    pass

    print(table)
    return True


def get_match_score(table, larger_rule, smaller_rule):
    matches: List[float] = [0 for _ in larger_rule]

    for index, rhs_rule_a in enumerate(larger_rule):
        for rhs_rule_b in smaller_rule:
            match = get_rhs_rule_match_score(table, rhs_rule_a, rhs_rule_b)
            matches[index] = max(match, matches[index])

    return sum(matches) / len(matches)


def get_rhs_rule_match_score(table, rule_a, rule_b) -> float:
    if type(rule_a) == type(rule_b):
        if type(rule_a) is tuple:
            if table[rule_a[0], rule_b[0]] < 0 or table[rule_a[1], rule_b[1]] < 0:
                raise UnknownValueError
            return table[rule_a[0], rule_b[0]] * table[rule_a[1], rule_b[1]]
        else:
            if rule_a == rule_b:
                return 1
    return 0


def is_matching_cfg_wrapper_10palindrome(max_depth):
    return is_matching_cfg(cnf_10palindrome, cnf_10palindrome, alphabet10, max_depth)


if __name__ == '__main__':
    is_matching_cfg_wrapper_10palindrome(3)
