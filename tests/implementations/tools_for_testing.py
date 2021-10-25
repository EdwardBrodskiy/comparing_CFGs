from tools import words_of_length
from implementations.lark_testing import is_accepted, cnf_10palindrome as lark_cnf
from typing import Iterator, Tuple, List
from copy import deepcopy
from cfg import CFG


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


def inject_type_1_errors(cfg: CFG):
    bad_cfg = deepcopy(cfg)
    for key, rhs in cfg.rules.items():
        for i in range(len(rhs)):
            temp = bad_cfg.rules[key].pop(i)
            yield bad_cfg
            bad_cfg.rules[key].insert(i, temp)
