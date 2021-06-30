from tools import words_of_length
from cfg import convert_rules_to_list, cfg_type
from typing import Dict
import numpy as np


def main():
    import cProfile
    import pstats

    with cProfile.Profile() as pr:
        is_matching_cfg_wrapper_10palindrome(15)

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.dump_stats(filename='memo_profiling.prof')


def parse(chars, rules, memo: Dict[str, np.array], start='S'):
    """
    CYK parser based on: https://en.wikipedia.org/wiki/CYK_algorithm#Algorithm
    """
    rules = convert_rules_to_list(rules)

    n = len(chars)
    no_rules = len(rules)
    memo_key = ''.join(chars)

    table = [[set() for _ in range(n - depth)] for depth in range(n)]
    table = np.zeros((n, n, no_rules), dtype=np.uint8)
    if memo_key[:-1] in memo:
        table[:-1, :-1, :] = memo[memo_key[:-1]]

    # Identify terminal rules
    for symbol_key, rule in enumerate(rules):
        for rhs in rule:
            if rhs == chars[-1]:
                table[0, -1, symbol_key] = 1
                break

    # fill the rest of the table
    for span in range(1, n):  # starting at the row after the terminals
        span_start = n - span - 1  # In other words column
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
    memo[memo_key] = table
    return table[-1, 0, 0] == 1


def is_matching_cfg(a, b, alphabet, max_depth: int):
    memo_a = {}
    memo_b = {}  # TODO: Note the way we are looking at it we only need to store the words of length - 1
    for depth in range(max_depth):
        for word in words_of_length(depth, alphabet):
            if parse(word, a, memo_a) != parse(word, b, memo_b):
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
    main()
