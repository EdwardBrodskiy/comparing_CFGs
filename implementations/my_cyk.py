from tools import words_of_length
from cfg import cnf_10palindrome, alphabet10


def parse(chars, rules, start='S'):
    """
    CYK parser based on: https://en.wikipedia.org/wiki/CYK_algorithm#Algorithm
    """
    n = len(chars)
    table = [[set() for _ in range(n - depth)] for depth in range(n)]

    # Identify terminal rules
    for char_index, char in enumerate(chars):
        for symbol_key, rule in rules.items():
            for rhs in rule:
                if rhs == char:
                    table[0][char_index].add(symbol_key)
                    break

    # fill the rest of the table
    for span in range(1, n):  # starting at the row after the terminals
        for span_start in range(n - span):  # In other words column
            for partition in range(span):  # Iterator for selecting combinations of squares for the left and right sides
                # check all the rules Ra -> Rb Rc
                for key, rule in rules.items():
                    for rhs in rule:
                        if type(rhs) is tuple:
                            left_side = rhs[0] in table[partition][span_start]
                            right_side = rhs[1] in table[span - partition - 1][span_start + partition + 1]
                            if left_side and right_side:
                                table[span][span_start].add(key)
    return start in table[-1][0]


def is_matching_cfg(a, b, alphabet, max_depth: int):
    for depth in range(max_depth + 1):
        for word in words_of_length(depth, alphabet):
            if parse(word, a) != parse(word, b):
                return False
    return True


def is_matching_cfg_wrapper_10palindrome(max_depth):
    return is_matching_cfg(cnf_10palindrome, cnf_10palindrome, alphabet10, max_depth)
