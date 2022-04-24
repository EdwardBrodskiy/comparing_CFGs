from tools import list_cnf_type
from dataclasses import dataclass
from typing import Tuple, Union


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
    print(' '.join(state.word))
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


def main():
    from cfg import cnf_10palindrome
    from tools import convert_cnf_to_list, convert_to_cnf, read_gram_file
    a_cnf = convert_to_cnf(read_gram_file(r'..\benchmarks\AntlrJavaGrammar.gram'))
    cnf_list = convert_cnf_to_list(a_cnf)
    seq = sequence(cnf_list, max_depth=7)
    print(f'\n\n{len(seq)=}')
    mean_length = round(sum(map(lambda state: len(state.word), seq)) / len(seq), 2)
    print(f'{mean_length=}')
    len_7 = len(list(filter(lambda state: len(state.word) == 7, seq)))
    print(f'{len_7=}')
    max_length = max(seq, key=lambda state: len(state.word))
    min_length = min(seq, key=lambda state: len(state.word))
    print(f'{max_length=} and {min_length=}')
    print(f'{len(max_length.word)=} and {len(min_length.word)=}')


if __name__ == '__main__':
    main()
