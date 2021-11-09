from typing import List, Tuple

import numpy as np
import heapq
from dataclasses import dataclass, field

from cfg import convert_cnf_to_list, cfg_rhs, cnf_10palindrome, CFG
from implementations.my_cyk_numpy import parse


class UnknownValueError(Exception):
    pass


@dataclass(order=True)
class Node:
    similarity: float
    string: Tuple = field(compare=False)
    difference_values: List = field(compare=False)
    # parent: Optional[Tuple] = field(compare=False)


def main():
    import cProfile
    import pstats
    from tools import convert_to_cnf, read_gram_file
    start, cfg = read_gram_file(r'..\benchmarks\C11Grammar1-1-1.gram')
    cnf = convert_to_cnf(start, cfg)
    with cProfile.Profile() as pr:
        is_matching_cfg_test(cnf, cnf, 1, generate_similarity_table_by_value_approach)
    stats = pstats.Stats(pr)
    stats.dump_stats(filename='analyzer.prof')

    with cProfile.Profile() as pr:
        is_matching_cfg_test(cnf, cnf, 1, modified)
    stats = pstats.Stats(pr)
    stats.dump_stats(filename='analyzer.prof')


def is_matching_cfg(a: CFG, b: CFG, max_depth: int):
    return is_matching_cfg_test(a, b, max_depth, modified)


def is_matching_cfg_test(a: CFG, b: CFG, max_depth: int, table_generator):
    memo_b = {}
    a_rule_set = convert_cnf_to_list(a)
    b_rule_set = convert_cnf_to_list(b)
    table = table_generator(a_rule_set, b_rule_set)

    a_max_list = table.max(axis=0)

    forest = {(0,)}

    heap: List[Node] = [Node(table[0, 0], (0,), get_similarity_values(a_max_list, (0,)))]  # start with S

    difference_found = False

    while not difference_found and len(heap):
        current_node = heap[0]
        smallest_match = 2
        sm_match_index = -1
        for i, diff in enumerate(current_node.difference_values):
            if diff is not None and diff < smallest_match:
                smallest_match = diff
                sm_match_index = i
        if sm_match_index == -1:
            heapq.heappop(heap)
        else:
            rule = a_rule_set[current_node.string[sm_match_index]]
            current_node.difference_values[sm_match_index] = None  # Mark as path traversed
            for rhs in rule:
                if type(rhs) is tuple:
                    new_string = current_node.string[:sm_match_index] + rhs + current_node.string[sm_match_index + 1:]
                else:
                    new_string = current_node.string[:sm_match_index] + (rhs,) + current_node.string[sm_match_index + 1:]
                    if all(map(lambda x: type(x) is str, new_string)):  # if all terminated
                        if not parse(new_string, b_rule_set):
                            difference_found = True
                            break
                if len(new_string) <= max_depth:  # TODO: that may be one too deep
                    if new_string not in forest:  # TODO: this shouldn't happen right but it does!?
                        heapq.heappush(heap, Node(current_node.similarity + smallest_match, new_string,
                                                  get_similarity_values(a_max_list, new_string)))
                        forest.add(new_string)
        # print(heap[0])
    return not difference_found


def get_similarity_values(best_matches, string):
    output = []
    for rule in string:
        if type(rule) is not str:
            output.append(best_matches[rule])
        else:
            output.append(None)
    return output


def generate_similarity_table(a, b):
    """
    Calculate values by assuming undefined values to be 1 when in cheat mode
    """
    table = np.ones([len(a), len(b)], dtype=np.float16) * -1  # table of -1's
    successful_comparison = True
    cheat_on_next = False  # TODO: should really cheat on the one with least undefined rules not the first one
    cheat_stack = []
    counter = 0
    success = 0

    while successful_comparison or not cheat_on_next:
        counter += 1
        print(f'{counter=} {success=}')
        cheat_on_next = not successful_comparison
        successful_comparison = False
        if cheat_on_next:
            pass
        for rule_a_index in range(1, len(a)):
            for rule_b_index in range(1, len(b)):
                if table[rule_a_index, rule_b_index] < 0:
                    rhs_a = a[rule_a_index]
                    rhs_b = b[rule_b_index]
                    try:
                        table[rule_a_index, rule_b_index] = get_match_score(table, rhs_a, rhs_b, cheat_on_next)
                        success += 1
                        successful_comparison = True
                        cheat_on_next = False
                    except UnknownValueError:
                        cheat_stack.append((rule_a_index, rule_b_index))

    table[0, 0] = get_match_score(table, a[0], b[0], True)

    return table


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


def modified(a, b):
    """
    Approach solution by continuously re calculating the similarity table starting with everything at 0
    """
    table = np.zeros([len(a) + 1, len(b) + 1], dtype=np.float16)
    for _ in range(3):  # TODO: change this to check for how much the change happened
        for rule_a_index in range(1, len(a)):
            for rule_b_index in range(1, len(b)):
                if not (table[-1, rule_b_index] > .9 or table[rule_a_index, -1] > .9):
                    rhs_a = a[rule_a_index]
                    rhs_b = b[rule_b_index]
                    table[rule_a_index, rule_b_index] = mod_get_match_score(table, rhs_a, rhs_b, False)
                    table[rule_a_index, -1] = table[rule_a_index, rule_b_index]
                    table[-1, rule_b_index] = table[rule_a_index, rule_b_index]

    table[0, 0] = mod_get_match_score(table, a[0], b[0], True)

    return table


def mod_get_match_score(table, rule_a: cfg_rhs, rule_b: cfg_rhs, cheat: bool) -> float:
    if len(rule_a) > len(rule_b):
        return mod_get_match_score_ls(table, rule_a, rule_b, cheat)
    return mod_get_match_score_ls(table, rule_b, rule_a, cheat)


def mod_get_match_score_ls(table, larger_rule, smaller_rule, cheat):
    matches: List[float] = [0 for _ in larger_rule]

    for index, rhs_rule_a in enumerate(larger_rule):
        for rhs_rule_b in smaller_rule:
            match = mod_get_rhs_rule_match_score(table, rhs_rule_a, rhs_rule_b, cheat)
            matches[index] = max(match, matches[index])

    return sum(matches) / len(matches)


def mod_get_rhs_rule_match_score(table, rule_a, rule_b, cheat) -> float:
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


if __name__ == '__main__':
    main()
