from tools import words_of_length
from cfg import convert_cnf_to_list, cnf_10palindrome, CFG
from typing import Dict, Tuple, Set


def parse(chars, rules, memo: Dict[Tuple, Set]) -> bool:
    result = wrapped_parse(chars, rules, memo)
    return 0 in result


def wrapped_parse(chars, rules, memo: Dict[Tuple, Set]) -> Set:
    n = len(chars)
    chars = tuple(chars)

    if chars in memo:
        return memo[chars]

    accepted = set()

    if n == 1:  # check rules that lead to this terminal
        for key, rhs in enumerate(rules):
            for rule in rhs:
                if type(rule) is str:
                    if chars[0] == rule:
                        accepted.add(key)
                        break
    else:
        for i in range(1, n):
            # split word in two in every possible way
            left, right = chars[:i], chars[i:]
            left_accepted, right_accepted = wrapped_parse(left, rules, memo), wrapped_parse(right, rules, memo)
            # find all the non-terminals that produce accepted left right pairs
            for key, rhs in enumerate(rules):
                for rule in rhs:
                    if type(rule) is tuple:
                        if rule[0] in left_accepted and rule[1] in right_accepted:
                            accepted.add(key)
                            break
    memo[chars] = accepted
    return accepted


def is_matching_cfg(a: CFG, b: CFG, max_depth: int):
    memo_a = {}
    memo_b = {}

    a_rule_set = convert_cnf_to_list(a)
    b_rule_set = convert_cnf_to_list(b)
    for depth in range(max_depth + 1):
        for word in words_of_length(depth, a.alphabet):
            if parse(word, a_rule_set, memo_a) != parse(word, b_rule_set, memo_b):
                return False
    return True


def main():
    pass


if __name__ == '__main__':
    main()
