from tools import words_of_length
from cfg import count_cfg_rules, CFG
from typing import Dict, Tuple, List
import numpy as np


def main():
    cfg = CFG(
        rules={
            'S': [('F',), ('(', 'S', '+', 'F', ')')],
            'F': ['a']
        },
        alphabet={'(', ')', 'a', '+'},
        start='S'
    )
    print(parse(list('(a+a)'), cfg))


def parse(chars: List[str], cfg: CFG):
    # we need ordered data structures to reference them in the table by index
    terminals_ref = list(cfg.alphabet)
    rules_ordered_ref = list(cfg.rules.keys())

    table = generate_parsing_table(rules_ordered_ref, terminals_ref, cfg)

    stack = [cfg.start]
    pos_in_chars = 0
    while stack:
        top = stack.pop()
        # Deal with a terminal
        if top in cfg.alphabet:
            if top == chars[pos_in_chars]:
                pos_in_chars += 1
                continue
            return False
        # Try to expand a non terminal
        top_index = rules_ordered_ref.index(top)
        next_index = table[top_index, terminals_ref.index(chars[pos_in_chars])]
        if next_index == -1:
            return False
        stack += reversed(cfg.rules[top][next_index])

    return len(chars) == pos_in_chars


def generate_parsing_table(rules_list, terminals, cfg: CFG):
    table = np.ones((len(rules_list), len(terminals)), dtype=np.int16) * -1
    for key_i, key in enumerate(rules_list):
        for term_i, term in enumerate(terminals):
            compute_loc(key_i, key, 0, term_i, term, count_cfg_rules(cfg.rules) + 1, table, cfg, rules_list)

    return table


def compute_loc(key_i: int, key: str, sub_rule_index: int, term_i: int, term: str, depth: int, table: np.array, cfg: CFG,
                rules_list: List[str]):
    if table[key_i, term_i] != -1 or depth == 0:
        return

    if key in cfg.alphabet:
        if key == term:
            table[key_i, term_i] = sub_rule_index
    else:
        for index, rule in enumerate(cfg.rules[key]):
            if type(rule) is tuple:
                rule = rule[0]
            if rule in cfg.alphabet:
                compute_loc(key_i, rule, index, term_i, term, depth - 1, table, cfg, rules_list)
            else:
                sub_rule_key = rule
                sub_rule_key_i = rules_list.index(rule)
                compute_loc(sub_rule_key_i, sub_rule_key, index, term_i, term, depth - 1, table, cfg, rules_list)
                if table[sub_rule_key_i, term_i] != -1:
                    table[key_i, term_i] = index
                    break


def is_matching_cfg(a: CFG, b: CFG, max_depth: int):
    for depth in range(max_depth + 1):
        for word in words_of_length(depth, a.alphabet):
            if parse(word, a) != parse(word, b):
                return False
    return True


if __name__ == '__main__':
    main()
