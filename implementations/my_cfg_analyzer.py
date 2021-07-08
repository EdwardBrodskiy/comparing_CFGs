from cfg import cnf_10palindrome, alphabet10, convert_rules_to_list, cfg_rhs
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
    successful_comparison = True
    cheat_on_next = False  # TODO: should really cheat on the one with least undefined rules not the first one
    while successful_comparison or not cheat_on_next:
        cheat_on_next = not successful_comparison
        successful_comparison = False
        for rule_a_index in range(1, len(a)):
            for rule_b_index in range(1, len(b)):
                if table[rule_a_index, rule_b_index] < 0:
                    rhs_a = a[rule_a_index]
                    rhs_b = b[rule_b_index]
                    try:
                        table[rule_a_index, rule_b_index] = get_match_score(table, rhs_a, rhs_b, cheat_on_next)
                        successful_comparison = True
                        cheat_on_next = False
                    except UnknownValueError:
                        pass

    table[0, 0] = get_match_score(table, a[0], b[0], True)

    return table[0, 0] == 1


def is_matching_cfg_nikos(a, b, alphabet, max_depth: int):
    memo_a = {}
    memo_b = {}
    a = convert_rules_to_list(a)
    b = convert_rules_to_list(b)
    table = np.zeros([len(a), len(b)], dtype=np.float16)
    successful_comparison = True
    cheat_on_next = False  # TODO: should really cheat on the one with least undefined rules not the first one
    for _ in range(100):
        cheat_on_next = not successful_comparison
        successful_comparison = False
        for rule_a_index in range(1, len(a)):
            for rule_b_index in range(1, len(b)):

                rhs_a = a[rule_a_index]
                rhs_b = b[rule_b_index]
                try:
                    table[rule_a_index, rule_b_index] = get_match_score(table, rhs_a, rhs_b, cheat_on_next)
                    successful_comparison = True
                    cheat_on_next = False
                except UnknownValueError:
                    pass

    table[0, 0] = get_match_score(table, a[0], b[0], True)
    print(table)
    return table[0, 0] == 1


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


def is_matching_cfg_wrapper_10palindrome(max_depth):
    return is_matching_cfg(cnf_10palindrome, cnf_10palindrome, alphabet10, max_depth)


if __name__ == '__main__':
    print(is_matching_cfg_wrapper_10palindrome(3))
