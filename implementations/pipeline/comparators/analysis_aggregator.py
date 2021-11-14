from typing import List, Tuple
import heapq
from dataclasses import dataclass, field

from cfg import CFG
from implementations.pipeline.pipeline_tools import PipelineDataManager, PipelineMethodData
from implementations.my_cyk_numpy import parse

from implementations.pipeline.analyzers import rhs_lengths, subrule_match, subrule_match_optimized


@dataclass(order=True)
class Node:
    similarity: float  # sum of all best match value scores for all rules used to construct the string
    used_rules: Tuple[int, ...] = field(compare=False)
    string: Tuple = field(compare=False)  # combination of rules and terminals basically the current construction
    difference_values: List = field(compare=False)  # a parallel list to "string" containing best match scores for each rule in "string"
    # parent: Optional[Tuple] = field(compare=False)


def symmetric_tree_search(a: CFG, b: CFG, max_depth: int, pipeline: PipelineDataManager) -> Tuple[bool, float]:
    a_decision, a_certainty = search_tree_from_tables(a, b, max_depth, pipeline, True)
    b_decision, b_certainty = search_tree_from_tables(a, b, max_depth, pipeline, False)
    # if either found a difference
    if a_decision is False or b_decision is False:
        return False, 1
    # if both are certain of equivalence (both have completed an exhaustive search)
    if a_certainty == 1 and b_certainty == 1:
        return True, 1
    # check is not complete and no difference is found (certainty calculation is currently redundant but is there for future proofing)
    return True, (a_certainty + b_certainty) / 2


def search_tree_from_tables(a: CFG, b: CFG, max_depth: int, pipeline: PipelineDataManager, use_a_as_base) -> Tuple[bool, float]:
    memory_key = method.key_word + str(use_a_as_base)
    if use_a_as_base:
        a_rule_set, b_rule_set = pipeline.list_rules
    else:
        b_rule_set, a_rule_set = pipeline.list_rules

    # which algorithms table output we prefer to use in descending order
    priority_list = [subrule_match.method.key_word, subrule_match_optimized.method.key_word, rhs_lengths.method.key_word]
    # decide what table to use
    table = None
    chosen_index = len(priority_list) - 1
    for i, option in enumerate(priority_list):
        if option in pipeline.tables:
            table = pipeline.tables[option]
            chosen_index = i
            break
    if table is None:
        raise ModuleNotFoundError
    certainty = (len(priority_list) - chosen_index) / len(priority_list)

    if not use_a_as_base:
        table = table.transpose()
    # get the best similarity value for each rule in A out of all the rules in b
    a_max_list = table.max(axis=0)

    checked_strings = {(0,)}  # keeps track of "string"s that were already looked at including ones that were removed from the heap

    # the heap is used to determine which should be the next Node to look at based on the lowest similarity
    heap: List[Node] = [Node(table[0, 0], (0,), (0,), get_similarity_values(a_max_list, (0,)))]  # start with S

    if memory_key in pipeline.data:  # results from search tree run earlier in the pipeline
        checked_strings, heap = pipeline.data[memory_key]
        # re do all of the calculations for similarity using the new table
        for node in heap:
            node.similarity = sum(map(lambda x: a_max_list[x], node.used_rules))
        heapq.heapify(heap)

    difference_found = False
    computation_counter = 0
    next_method_complexity = pipeline.get_next_method_complexity()
    while not difference_found and len(heap) and computation_counter * 2 < next_method_complexity:
        current_node = heap[0]

        # TODO: there must be a better way to get the min
        smallest_match = 2
        sm_match_index = -1
        for i, diff in enumerate(current_node.difference_values):
            if diff is not None and diff < smallest_match:
                smallest_match = diff
                sm_match_index = i

        if sm_match_index == -1:  # if all branches have been looked at remove it
            heapq.heappop(heap)
        else:
            rhs = a_rule_set[current_node.string[sm_match_index]]
            current_node.difference_values[sm_match_index] = None  # Mark as path traversed
            for sub_rule in rhs:
                # insert sub_rule into string
                if type(sub_rule) is tuple:
                    new_string = current_node.string[:sm_match_index] + sub_rule + current_node.string[sm_match_index + 1:]

                else:
                    new_string = current_node.string[:sm_match_index] + (sub_rule,) + current_node.string[sm_match_index + 1:]
                    if all(map(lambda x: type(x) is str, new_string)):  # if all terminals i.e. final string
                        computation_counter += len(new_string) ** 2
                        if not parse(new_string, b_rule_set):  # check if rule set B accepts the found string
                            difference_found = True
                            break
                # add the new string to the heap for further development
                if len(new_string) <= max_depth:  # TODO: that may be one too deep
                    if new_string not in checked_strings:  # TODO: this shouldn't happen right but it does!? or should it?
                        heapq.heappush(heap, Node(current_node.similarity + smallest_match,
                                                  (*current_node.used_rules, current_node.string[sm_match_index]), new_string,
                                                  get_similarity_values(a_max_list, new_string)))
                        checked_strings.add(new_string)
    if difference_found:
        return False, 1
    # TODO: needs to be done with respect of B to A for this to properly work as we may miss strings accepted by B but not by A
    elif len(heap) == 0:
        return True, 1
    pipeline.data[memory_key] = checked_strings, heap
    return True, certainty


def complexity_of_search_tree_from_tables(a: CFG, b: CFG, max_depth: int) -> int:
    return 1


method = PipelineMethodData(
    symmetric_tree_search,
    complexity_of_search_tree_from_tables,
    'search_tree_from_tables'
)


def get_similarity_values(best_matches, string):
    output = []
    for rule in string:
        if type(rule) is not str:  # if not a terminal
            output.append(best_matches[rule])
        else:
            output.append(None)
    return output
