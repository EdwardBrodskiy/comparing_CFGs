from typing import List, Tuple, Optional
import heapq
from dataclasses import dataclass, field
import logging
from math import inf

from cfg import CFG
from implementations.pipeline.pipeline_tools import PipelineDataManager, PipelineMethodData
from implementations.my_cyk_numpy import parse

from implementations.pipeline.analyzers import rhs_lengths, subrule_match, subrule_match_optimized


@dataclass(order=True)
class Node:
    priority: float
    similarity: float = field(compare=False)  # sum of all best match value scores for all rules used to construct the string
    used_rules: Tuple[int, ...] = field(compare=False)
    string: Tuple = field(compare=False)  # combination of rules and terminals basically the current construction
    difference_values: List = field(compare=False)  # a parallel list to "string" containing best match scores for each rule in "string"
    # parent: Optional[Tuple] = field(compare=False)


class Analyzer:
    def __init__(self, a: CFG, b: CFG, max_depth: int):
        self._a = a
        self._b = b
        self._a_searcher, self._b_searcher = None, None
        self._max_depth = max_depth
        self._pipeline = None

    def set_pipeline(self, pipeline: PipelineDataManager):
        self._pipeline = pipeline
        self._a_searcher = Searcher(self._a, self._b, self._max_depth, pipeline, True)
        self._b_searcher = Searcher(self._a, self._b, self._max_depth, pipeline, False)

    def symmetric_tree_search(self, *args, **kwargs) -> Tuple[bool, float]:
        if self._pipeline is None:
            raise Exception('Please set pipeline')
        # if either found a difference means we found a counter example
        logging.info('Checking if words in grammar A are present in grammar B')
        a_decision, a_certainty = self._a_searcher.search()
        if a_decision is False:
            return False, 1

        logging.info('Checking if words in grammar B are present in grammar A')
        b_decision, b_certainty = self._b_searcher.search()
        if b_decision is False:
            return False, 1

        # if both are certain of equivalence (both have completed an exhaustive search)
        if a_certainty == 1 and b_certainty == 1:
            return True, 1
        # check is not complete and no difference is found (certainty calculation is currently redundant but is there for future proofing)
        return True, (a_certainty + b_certainty) / 2


class Searcher:
    def __init__(self, a: CFG, b: CFG, max_depth: int, pipeline: PipelineDataManager, use_a_as_base):
        self.max_depth = max_depth
        self.pipeline = pipeline
        self.use_a_as_base = use_a_as_base

        self.memory_key = method.key_word + str(use_a_as_base)
        if self.use_a_as_base:
            self.a_rule_set, self.b_rule_set = pipeline.list_rules
            self.proximity_to_terminal, _ = pipeline.terminal_distances
        else:
            self.b_rule_set, self.a_rule_set = pipeline.list_rules
            _, self.proximity_to_terminal = pipeline.terminal_distances

        self.checked_strings = {(0,)}  # keeps track of "string"s that were already looked at including ones that were removed from the heap

        # the heap is used to determine which should be the next Node to look at based on the lowest similarity
        self.heap: Optional[List[Node]] = None

    def search(self) -> Tuple[bool, float]:
        # which algorithms table output we prefer to use in descending order
        priority_list = [subrule_match.method.key_word, subrule_match_optimized.method.key_word, rhs_lengths.method.key_word]
        # decide what table to use
        table = None
        chosen_index = len(priority_list) - 1
        for i, option in enumerate(priority_list):
            if option in self.pipeline.tables:
                table = self.pipeline.tables[option]
                chosen_index = i
                break
        if table is None:
            raise ModuleNotFoundError
        certainty = self.calculate_certainty(priority_list, chosen_index)

        if self.use_a_as_base:
            table = table.transpose()
        # get the best similarity value for each rule in A out of all the rules in b
        max_list = table.max(axis=0)

        combined_weight = max_list * (self.proximity_to_terminal * 10)

        # the heap is used to determine which should be the next Node to look at based on the lowest similarity
        if self.heap is None:  # start with S
            self.heap = [Node(table[0, 0], table[0, 0], (0,), (0,), self.get_similarity_values(combined_weight, (0,)))]

        difference_found = False
        computation_counter = 0
        next_method_complexity = self.pipeline.get_next_method_complexity()
        while not difference_found and len(self.heap) and computation_counter * 2 < next_method_complexity:
            current_node = self.heap[0]

            sm_match_index = min(range(len(current_node.difference_values)),
                                 key=lambda index: current_node.difference_values[index] if current_node.difference_values[
                                                                                                index] is not None else inf)
            smallest_match: float = current_node.difference_values[sm_match_index]
            if smallest_match is None:
                heapq.heappop(self.heap)
                continue
            rhs = self.a_rule_set[current_node.string[sm_match_index]]
            current_node.difference_values[sm_match_index] = None  # Mark as path traversed
            for sub_rule in rhs:
                # insert sub_rule into string
                if type(sub_rule) is tuple:
                    new_string = current_node.string[:sm_match_index] + sub_rule + current_node.string[sm_match_index + 1:]

                else:
                    new_string = current_node.string[:sm_match_index] + (sub_rule,) + current_node.string[sm_match_index + 1:]
                    if all(map(lambda x: type(x) is str, new_string)):  # if all terminals index.e. final string
                        computation_counter += len(new_string) ** 2
                        # TODO: can save words checked so that cfgb does not check them again
                        if not parse(new_string, self.b_rule_set):  # check if rule set B accepts the found string
                            difference_found = True
                            logging.info(f'tree search found counter example: {" ".join(new_string)}')
                            break
                        else:
                            logging.info(f'checked {"".join(new_string)}')
                        self.checked_strings.add(new_string)
                        continue  # don't add word to heap
                # add the new string to the heap for further development
                if len(new_string) <= self.max_depth:  # TODO: that may be one too deep
                    if new_string not in self.checked_strings:
                        similarity = current_node.similarity + smallest_match
                        number_of_terminals = len(tuple(filter(lambda x: type(x) is str, new_string))) + 1
                        computation_counter += len(new_string)
                        heapq.heappush(self.heap, Node(similarity / number_of_terminals, similarity,
                                                       (*current_node.used_rules, current_node.string[sm_match_index]), new_string,
                                                       self.get_similarity_values(combined_weight, new_string)))
                        self.checked_strings.add(new_string)
        if difference_found:
            return False, 1
        elif len(self.heap) == 0:
            return True, 1
        self.pipeline.data[self.memory_key] = self.checked_strings, self.heap
        return True, certainty

    @staticmethod
    def get_similarity_values(weightings, string):
        output = []
        for rule in string:
            if type(rule) is not str and weightings[rule] >= 0:  # if not a terminal
                output.append(weightings[rule])
            else:
                output.append(None)
        return output

    @staticmethod
    def calculate_certainty(options_list, selected_index):
        return (len(options_list) - selected_index) / len(options_list)


def complexity_of_search_tree_from_tables(a: CFG, b: CFG, max_depth: int) -> int:
    return 1


method = PipelineMethodData(
    None,
    complexity_of_search_tree_from_tables,
    'search_tree_from_tables'
)
