from tools import words_of_length
from implementations.lark_testing import is_accepted, cnf_10palindrome as lark_cnf
from typing import Iterator, Tuple, List
from copy import deepcopy
from cfg import CFG
import random
import logging


# intended to be something to compare against as all the code is not writen by me
def word_and_result_from_nltk_10palindrome(max_depth) -> Iterator[Tuple[List[str], bool]]:
    for length in range(max_depth):
        for word in words_of_length(length, ['1', '0']):
            joined_word = ''.join(word)
            yield word, is_accepted(lark_cnf, joined_word)


'''
From Automating Grammar Comparison

Type 1 Errors. We construct Gm by removing one production of G chosen at random. In this case, L(Gm) 
⊆ L(G). The inclusion is proper only if the production that is removed is not redundant.

Type 2 Errors. We create Gm by choosing (at random) one production of G having at least two non-terminals, 
and removing (at random) one non-terminal from the righthand-side. In this case, neither L(Gm) nor L(G) has 
to necessarily include the other.

Type 3 Errors. We construct Gm as follows. We randomly choose one production of the grammar, say P, having at 
least two non-terminals, and also choose one non-terminal of the right-hand-side, say N. We then create rule_a copy 
(say N0) of the non-terminal N that has every production of N except one (determined at random). We replace N 
by N0 in the production P.
'''


def inject_type_1_errors(cfg: CFG, sample_size=10, be_consistent=True, seed=42):  # takes cfg in cnf form
    if be_consistent:
        rnd = random.Random(seed)
    else:
        rnd = random

    bad_cfg = deepcopy(cfg)
    alphabet_count = get_terminal_count(bad_cfg)

    sub_rule_count = sum(map(lambda x: len(bad_cfg.rules[x]), bad_cfg.rules))
    selected_indices = None
    # for the case when the sample size is larger than the number of sub rules all will be used
    if sample_size < sub_rule_count:
        selected_indices = set(rnd.sample(range(sub_rule_count), sample_size))
    logging.info(f'inject type 1 errors is looking at {selected_indices}')

    index = 0
    for key, rhs in cfg.rules.items():
        for i in range(len(rhs)):
            if selected_indices is None or index in selected_indices:
                temp = bad_cfg.rules[key].pop(i)
                if type(temp) is str and alphabet_count[temp] == 1:
                    bad_cfg.alphabet.remove(temp)
                yield bad_cfg
                bad_cfg.rules[key].insert(i, temp)
                if type(temp) is str:
                    bad_cfg.alphabet.add(temp)
            index += 1


# make a count up for the usage of each terminal
def get_terminal_count(cfg: CFG):  # TODO: find a way to ensure reachability
    alphabet = {key: 0 for key in cfg.alphabet}
    for key, rhs in cfg.rules.items():
        for rule in rhs:
            if type(rule) is str:
                alphabet[rule] += 1
    return alphabet
