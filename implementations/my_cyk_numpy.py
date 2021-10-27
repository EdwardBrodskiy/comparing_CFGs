from tools import words_of_length
from cfg import convert_cnf_to_list, cnf_10palindrome, CFG
import numpy as np


def parse(chars, rules):
    """
    CYK parser based on: https://en.wikipedia.org/wiki/CYK_algorithm#Algorithm
    """

    n = len(chars)
    no_rules = len(rules)

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
                                # TODO: check if rule_a break here helps
    return table[-1, 0, 0] == 1


def is_matching_cfg(a: CFG, b: CFG, max_depth: int):
    a_rule_set = convert_cnf_to_list(a)
    b_rule_set = convert_cnf_to_list(b)
    for depth in range(max_depth + 1):
        for word in words_of_length(depth, a.alphabet):
            if parse(word, a_rule_set) != parse(word, b_rule_set):
                return False
    return True


if __name__ == '__main__':
    print(parse(['1', '1'], cnf_10palindrome))
