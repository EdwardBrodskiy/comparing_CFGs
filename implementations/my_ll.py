from tools import words_of_length, is_input_string_legal
from cfg import count_cfg_rules, CFG, cnf_10palindrome
from typing import Dict, Tuple, List
import numpy as np
import logging
from dataclasses import dataclass

ll_cfg = CFG(
    rules={
        'S': [('F',), ('(', 'S', '+', 'F', ')')],
        'F': ['a']
    },
    alphabet={'(', ')', 'a', '+'},
    start='S'
)


@dataclass
class PreCalculatedData:
    terminals_ref: List[str]
    rules_ordered_ref: List[str]
    table: np.array


def generate_pre_calculated_data(cfg: CFG):
    # we need ordered data structures to reference them in the table by index
    data = PreCalculatedData(
        terminals_ref=list(cfg.alphabet),
        rules_ordered_ref=list(cfg.rules.keys()),
        table=np.array([1])
    )
    data.table = generate_parsing_table(data.rules_ordered_ref, data.terminals_ref, cfg)
    return data


def main():
    import cProfile
    import pstats

    logging.basicConfig(filename='my_ll.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    data = generate_pre_calculated_data(ll_cfg)
    with cProfile.Profile() as pr:
        # is_matching_cfg(ll_cfg, ll_cfg, 2)
        parse(list('(((a+a)+a)+a)'), ll_cfg, data)
    stats = pstats.Stats(pr)
    stats.dump_stats(filename='my_ll.prof')


def parse(chars: List[str], cfg: CFG, data: PreCalculatedData):
    if not is_input_string_legal(chars, cfg):  # TODO: more efficient to make sure it can't happen at an earlier stage
        return False
    stack = [cfg.start]
    pos_in_chars = 0
    while stack and pos_in_chars < len(chars) and len(chars) - pos_in_chars >= len(stack):
        top = stack.pop()
        # Deal with a terminal
        if top in cfg.alphabet:
            if top == chars[pos_in_chars]:
                pos_in_chars += 1
                continue
            return False
        # Try to expand a non terminal
        top_index = data.rules_ordered_ref.index(top)
        next_index = data.table[top_index, data.terminals_ref.index(chars[pos_in_chars])]
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
            if not isinstance(rule, str):
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
    a_data = generate_pre_calculated_data(a)
    b_data = generate_pre_calculated_data(b)
    for depth in range(max_depth + 1):
        for word in words_of_length(depth, a.alphabet):
            if parse(word, a, a_data) != parse(word, b, b_data):
                return False
    return True


if __name__ == '__main__':
    main()
