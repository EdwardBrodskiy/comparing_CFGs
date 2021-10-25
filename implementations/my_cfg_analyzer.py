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
    pass


def is_matching_cfg(a: CFG, b: CFG, max_depth: int):
    memo_b = {}
    a_rule_set = convert_cnf_to_list(a)
    b_rule_set = convert_cnf_to_list(b)
    table = generate_similarity_table(a_rule_set, b_rule_set)

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

    return table


def generate_similarity_table_by_value_approach(a, b):
    """
    Approach solution by continuously re calculating the similarity table starting with everything at 0
    """
    table = np.zeros([len(a), len(b)], dtype=np.float16)
    for _ in range(100):  # TODO: change this to check for how much the change happened
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


if __name__ == '__main__':
    main()
