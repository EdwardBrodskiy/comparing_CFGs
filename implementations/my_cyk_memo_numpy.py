from tools import words_of_length
from cfg import convert_cnf_to_list, cnf_10palindrome, CFG
from typing import Dict, Tuple, Iterator
import numpy as np


def main():
    size = 10
    test = np.zeros((size, size), dtype=np.int32)
    for x in range(size):
        for y in range(size):
            if is_in_triangle((1, 1), 8, x, y, size):
                test[y, x] = 0
            else:
                test[y, x] = 100_000 + x * 100 + y

    print(test)


def parse(chars, rules, memo: Dict[Tuple, np.array]):
    """
    CYK parser based on: https://en.wikipedia.org/wiki/CYK_algorithm#Algorithm
    """

    n = len(chars)
    no_rules = len(rules)
    memo_key = tuple(chars)

    # table = [[set() for _ in range(n - depth)] for depth in range(n)]
    table = np.zeros((n, n, no_rules), dtype=np.bool8)

    # load the largest available sub word from memory
    loaded: Tuple[Tuple[int, int], int] = ((0, 0), 0)
    for sub_word, lower_bound, upper_bound in permutations_of_cuts(memo_key):
        if sub_word in memo:
            table[lower_bound:upper_bound, lower_bound:upper_bound, :] = np.logical_or(
                table[lower_bound:upper_bound, lower_bound:upper_bound, :], memo[sub_word])
            loaded = ((lower_bound, 0), upper_bound - lower_bound)
            break

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
                if is_in_triangle(loaded[0], loaded[1], span, span_start, len(chars)):
                    continue
                for rhs in rule_set:
                    if type(rhs) is tuple:
                        left_side = table[partition, span_start, rhs[0]]
                        right_side = table[span - partition - 1, span_start + partition + 1, rhs[1]]
                        if left_side and right_side:
                            table[span, span_start, key] = True
                            # TODO: check if rule_a break here helps
    memo[memo_key] = table
    return table[-1, 0, 0] == 1


def permutations_of_cuts(word: Tuple[str, ...]) -> Iterator[Tuple[Tuple[str, ...], int, int]]:
    for i in reversed(range(len(word))):
        for offset in range(len(word) - i):
            upper_bound = i + offset + 1
            yield word[offset:upper_bound], offset, upper_bound


def is_in_triangle(position: Tuple[int, int], width: int, x: int, y: int, size: int):
    if position[0] <= x <= position[0] + width and position[1] < size - y <= position[1] + width:
        if (x - position[0]) + (width - y - position[1]) + 1 < width:
            return True
    return False


def is_matching_cfg(a: CFG, b: CFG, max_depth: int):
    memo_a = {}
    memo_b = {}  # TODO: Note the way we are looking at it we only need to store the words of length - 1

    a_rule_set = convert_cnf_to_list(a)
    b_rule_set = convert_cnf_to_list(b)
    for depth in range(max_depth + 1):
        for word in words_of_length(depth, a.alphabet):
            if parse(word, a_rule_set, memo_a) != parse(word, b_rule_set, memo_b):
                return False
    return True


if __name__ == '__main__':
    main()
