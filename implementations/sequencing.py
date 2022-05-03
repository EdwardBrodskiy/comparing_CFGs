from tools import list_cnf_type, convert_cnf_to_list
from cfg import CFG, cnf_10palindrome
from dataclasses import dataclass
from typing import Tuple, Union
from implementations.my_cyk_memo import parse


@dataclass
class State:
    used_keys: Tuple[int, ...]
    word: Tuple[Union[int, str], ...]


def sequence(cnf: list_cnf_type, max_depth=10):
    state = State(tuple(), (0,))

    return sub_sequence(cnf, state, max_depth=max_depth)


def sub_sequence(cnf: list_cnf_type, state: State, max_depth):
    if len(state.word) > max_depth:
        return []
    skipped = []
    new_keys_found = set()
    for i, key in enumerate(state.word):
        if type(key) is int:
            if key not in state.used_keys and key not in new_keys_found:
                new_keys_found.add(key)
            else:
                skipped.append(i)
    if new_keys_found:
        new_state = State((*state.used_keys, *new_keys_found), state.word)
        return expand_all(cnf, new_state, 0, max_depth)
    if skipped:
        return []
    return [state]


def expand_all(cnf: list_cnf_type, state: State, start_index, max_depth):
    for i, key in enumerate(state.word[start_index:]):
        i += start_index
        if type(key) is int:
            new_states = []
            for rule in cnf[key]:
                if type(rule) is tuple:
                    new_word = (*state.word[:i], *rule, *state.word[i + 1:])
                    new_start = i + 2
                else:
                    new_word = (*state.word[:i], rule, *state.word[i + 1:])
                    new_start = i + 1
                new_states.append(expand_all(cnf, State(state.used_keys, new_word), new_start, max_depth))

            return [st for sub_states in new_states for st in sub_states]
    return sub_sequence(cnf, state, max_depth)


def generate_loop_extensions(words):
    extensions = set()
    for word in words:
        for end_index in range(1, len(word) + 1):
            for start_index in range(end_index):
                for insert_index in range(start_index, end_index + 1):
                    sub_word = word[start_index: end_index]
                    new_word = word[:insert_index] + sub_word + word[insert_index:]
                    extensions.add(new_word)
                    # print(f'old {" ".join(word)} new {" ".join(new_word)}')
    return extensions


def is_matching_cfg(a: CFG, b: CFG, max_depth: int):
    memo_a = {}
    memo_b = {}

    a_rule_set = convert_cnf_to_list(a)
    b_rule_set = convert_cnf_to_list(b)

    # create the non looping sequences for both grammars
    a_test_set = set(map(lambda state: state.word, sequence(a_rule_set, max_depth=max_depth)))
    b_test_set = set(map(lambda state: state.word, sequence(b_rule_set, max_depth=max_depth)))
    # combine them
    reduced_set = a_test_set.union(b_test_set)
    # produce every possible next step if any of the rules were a loop
    test_set = reduced_set.union(generate_loop_extensions(reduced_set))

    for word in test_set:
        if parse(word, a_rule_set, memo_a) != parse(word, b_rule_set, memo_b):
            return False
    return True


def main():
    from cfg import cnf_10palindrome
    from tools import convert_to_cnf, read_gram_file
    a_cnf = convert_to_cnf(read_gram_file(r'..\benchmarks\AntlrJavaGrammar.gram'))
    print(generate_loop_extensions([('1', '0', '1')]))


if __name__ == '__main__':
    main()
