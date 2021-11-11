from typing import Optional, List, Tuple
import heapq
from dataclasses import dataclass, field

from cfg import CFG
from implementations.pipeline.pipeline import Pipeline
from implementations.my_cyk_numpy import parse


@dataclass(order=True)
class Node:
    similarity: float
    string: Tuple = field(compare=False)
    difference_values: List = field(compare=False)
    # parent: Optional[Tuple] = field(compare=False)


def search_tree_from_tables(a: CFG, b: CFG, max_depth: int, pipeline: Pipeline) -> Optional[bool]:
    a_rule_set, b_rule_set = pipeline.list_rules

    priority_list = ['sub-rules', 'sub-rules-opt', 'rhs_lengths']
    table = None
    for option in priority_list:
        if option in pipeline.data:
            table = pipeline.data[option]
            break
    if table is None:
        raise ModuleNotFoundError

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

    return not difference_found


def get_similarity_values(best_matches, string):
    output = []
    for rule in string:
        if type(rule) is not str:
            output.append(best_matches[rule])
        else:
            output.append(None)
    return output
