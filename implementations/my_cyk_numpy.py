from tools import words_of_length
import numpy as np
from typing import Dict, List, Union, Tuple

cfg_type = Dict[str, List[Union[Tuple, str]]]


def parse(chars, rules, start='S'):
    """
    CYK parser based on: https://en.wikipedia.org/wiki/CYK_algorithm#Algorithm
    """
    rules = convert_rules_to_list(rules)

    n = len(chars)
    no_rules = len(rules)

    table = [[set() for _ in range(n - depth)] for depth in range(n)]
    table = np.zeros((n, n, no_rules), dtype=np.uint8)

    # Identify terminal rules
    for char_index, char in enumerate(chars):
        for symbol_key, rule in enumerate(rules):
            for rhs in rule:
                if rhs == char:
                    table[0, char_index, symbol_key] = 1
                    break

    # fill the rest of the table
    for span in range(1, n):  # starting at the row after the terminals
        for span_start in range(n - span):  # In other words column
            for partition in range(span):  # Iterator for selecting combinations of squares for the left and right sides
                # check all the rules Ra -> Rb Rc
                for key, rule_set in enumerate(rules):
                    for rhs in rule_set:
                        if type(rhs) is tuple:
                            left_side = table[partition, span_start, rhs[0]]
                            right_side = table[span - partition - 1, span_start + partition + 1, rhs[1]]
                            if left_side and right_side:
                                table[span, span_start, key] = 1
                                # TODO: check if a break here helps
    return table[-1, 0, 0] == 1


def convert_rules_to_list(rules: cfg_type):
    new_rules = [[] for _ in rules]
    mapping = {key: index for index, key in enumerate(rules.keys())}

    for key, rule in rules.items():
        new_rules[mapping[key]] = list(map(lambda rhs_rule: convert_rhs_rule(rhs_rule, mapping), rule))

    return new_rules


def convert_rhs_rule(rule, mapping):
    if type(rule) is tuple:
        return convert_value(rule[0], mapping), convert_value(rule[1], mapping)
    return convert_value(rule, mapping)


def convert_value(value, mapping):
    if value in mapping:
        return mapping[value]
    return value


def is_matching_cfg(a, b, alphabet, max_depth: int):
    for depth in range(max_depth):
        for word in words_of_length(depth, alphabet):
            if parse(word, a) != parse(word, b):
                return False
    return True


def is_matching_cfg_wrapper_10palindrome(max_depth):
    return is_matching_cfg(cnf_10palindrome, cnf_10palindrome, alph, max_depth)


alph = ['1', '0']

cnf_10palindrome: cfg_type = {
    # start
    'S': [('X', 'A'), ('Y', 'B'), '1', '0'],
    # base
    'D': [('X', 'A'), ('Y', 'B'), '1', '0'],
    # alterone
    'A': [('D', 'X')],
    # alterzero
    'B': [('D', 'Y')],
    # one
    'X': ['1'],
    # zero
    'Y': ['0']
}

if __name__ == '__main__':
    print(parse(['1', '1'], cnf_10palindrome))
