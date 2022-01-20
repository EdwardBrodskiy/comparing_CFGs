from tools import words_of_length
from cfg import convert_cnf_to_list, cnf_10palindrome, CFG
from typing import Dict, Tuple, List
import numpy as np


def main():
    parse(['1', '1'], cnf_10palindrome)


def parse(chars: List[str], cfg: CFG):
    terminals_ref = list(cfg.alphabet)
    rules_ordered_ref = list(cfg.rules.keys())
    table = generate_parsing_table(rules_ordered_ref, terminals_ref, cfg)
    print(table)
    return True


def generate_parsing_table(rules_list, terminals, cfg: CFG):
    table = np.ones((len(rules_list), len(terminals)), dtype=np.int16) * -1
    print(table)
    for key_i, key in enumerate(rules_list):
        for term_i, term in enumerate(terminals):
            compute_loc(key_i, key, term_i, term, 100, table, cfg, rules_list)

    return table


def compute_loc(key_i: int, key: str, term_i: int, term: str, depth: int, table: np.array, cfg: CFG, rules_list: List[str]):
    if table[key_i, term_i] != -1 or depth == 0:
        return

    if key in cfg.alphabet:
        if key == term:
            table[key_i, term_i] = key_i
    else:
        for rule in cfg.rules[key]:
            if type(rule) is str:
                compute_loc(key_i, rule, term_i, term, depth - 1, table, cfg, rules_list)
            else:  # TODO: currently assuming CNF fix
                sub_rule_key = rule[0]
                sub_rule_key_i = rules_list.index(rule[0])
                compute_loc(sub_rule_key_i, sub_rule_key, term_i, term, depth - 1, table, cfg, rules_list)
                if table[sub_rule_key_i, term_i] != -1:
                    table[key_i, term_i] = sub_rule_key_i
                    break


def is_matching_cfg(a: CFG, b: CFG, max_depth: int):
    for depth in range(max_depth + 1):
        for word in words_of_length(depth, a.alphabet):
            if parse(word, a) != parse(word, b):
                return False
    return True


if __name__ == '__main__':
    main()
