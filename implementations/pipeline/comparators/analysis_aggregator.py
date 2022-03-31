from typing import List, Tuple, Optional, Iterator
import heapq
from dataclasses import dataclass, field
import logging
from math import inf
import itertools
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
        self._checked_words = set()

    def set_pipeline(self, pipeline: PipelineDataManager):
        self._pipeline = pipeline

        a_rule_set, b_rule_set = self._pipeline.list_rules

        self._a_searcher = Searcher(a_rule_set, self._max_depth, pipeline, True)
        self._b_searcher = Searcher(b_rule_set, self._max_depth, pipeline, False)

    def symmetric_tree_search(self, *args, **kwargs) -> Tuple[bool, float]:
        if self._pipeline is None:
            raise Exception('Please set pipeline')

        a_rule_set, b_rule_set = self._pipeline.list_rules

        RUNNING_LENGTH = []
        # if either found a difference means we found a counter example
        for word_a, word_b, in itertools.zip_longest(self._a_searcher.search(), self._b_searcher.search()):
            # if the words are the same then they must be in both grammars so no parsing is required hence continue

            RUNNING_LENGTH.append((len(word_a) + len(word_b)) / 2)
            if not len(RUNNING_LENGTH) % 10:
                logging.debug(f'''words found: {len(RUNNING_LENGTH)}
running average length is {round(sum(RUNNING_LENGTH[-10:]) / 10, 2)} 
the total average is {round(sum(RUNNING_LENGTH) / len(RUNNING_LENGTH), 2)}
                               ''')
                logging.debug(f'{len(self._a_searcher.heap)=} {len(self._b_searcher.heap)=}')
            if word_a == word_b:
                self._checked_words.add(word_a)
                continue
            # check word a in grammar B
            if word_a is not None and word_a not in self._checked_words:
                if parse(word_a, b_rule_set):
                    return False, 1
                self._checked_words.add(word_a)
            # check word b in grammar A
            if word_b is not None and word_b not in self._checked_words:
                if parse(word_b, a_rule_set):
                    return False, 1
                self._checked_words.add(word_b)

        # if both are certain of equivalence (both have completed an exhaustive search)
        if self._a_searcher.certainty == 1 and self._b_searcher.certainty == 1:
            return True, 1
        # check is not complete and no difference is found (certainty calculation is currently redundant but is there for future proofing)
        return True, (self._a_searcher.certainty + self._b_searcher.certainty) / 2


class Searcher:
    def __init__(self, rule_set, max_depth: int, pipeline: PipelineDataManager, use_a_as_base):
        self.max_depth = max_depth
        self.pipeline = pipeline
        self.use_a_as_base = use_a_as_base

        self.memory_key = method.key_word + str(use_a_as_base)

        self.rule_set = rule_set

        self.checked_strings = {(0,)}  # keeps track of "string"s that were already looked at including ones that were removed from the heap

        # the heap is used to determine which should be the next Node to look at based on the lowest similarity
        self.heap: Optional[List[Node]] = None

        self._certainty: int = 0

    @property
    def certainty(self):
        return self._certainty

    def search(self) -> Iterator[List[str]]:
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

        combined_weight = max_list

        # the heap is used to determine which should be the next Node to look at based on the lowest similarity
        if self.heap is None:  # start with S
            self.heap = [Node(table[0, 0], table[0, 0], (), (0,), self.get_similarity_values(combined_weight, (0,)))]

        difference_found = False
        computation_counter = 0
        # next_method_complexity = self.pipeline.get_next_method_complexity()
        while not difference_found and len(self.heap):

            current_node = self.heap[0]

            # get the index of the smallest non None value for similarity out of current options
            sm_match_index = min(range(len(current_node.difference_values)),
                                 key=lambda index: current_node.difference_values[index] if current_node.difference_values[
                                                                                                index] is not None else inf)
            smallest_match: float = current_node.difference_values[sm_match_index]

            # If None was selected i.e. infinity == min this means there are no options left
            if smallest_match is None:
                heapq.heappop(self.heap)
                continue
            rhs = self.rule_set[current_node.string[sm_match_index]]
            current_node.difference_values[sm_match_index] = None  # Mark as path traversed
            for sub_rule in rhs:
                # insert sub_rule into string
                if type(sub_rule) is tuple:
                    new_string = current_node.string[:sm_match_index] + sub_rule + current_node.string[sm_match_index + 1:]

                else:
                    new_string = current_node.string[:sm_match_index] + (sub_rule,) + current_node.string[sm_match_index + 1:]
                    if all(map(lambda x: type(x) is str, new_string)):  # if all terminals index.e. final string
                        computation_counter += len(new_string) ** 2
                        self.checked_strings.add(new_string)
                        yield new_string

                        continue  # don't add word to heap
                # add the new string to the heap for further development
                if len(new_string) <= self.max_depth:  # TODO: that may be one too deep
                    if new_string not in self.checked_strings:
                        new_similarity = current_node.similarity + smallest_match
                        number_of_terminals = len(tuple(filter(lambda x: type(x) is str, new_string))) + 1
                        computation_counter += len(new_string)
                        new_priority = new_similarity / (number_of_terminals * len(new_string))
                        heapq.heappush(self.heap, Node(new_priority, new_similarity,
                                                       (*current_node.used_rules, current_node.string[sm_match_index]), new_string,
                                                       self.get_similarity_values(combined_weight, new_string)))
                        self.checked_strings.add(new_string)

        if len(self.heap) == 0:
            self._certainty = 1
        else:
            # TODO: check if this is still needed.
            self.pipeline.data[self.memory_key] = self.checked_strings, self.heap
            self._certainty = certainty

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
