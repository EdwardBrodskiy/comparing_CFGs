from implementations.agc.agc_enum import Enum
from cfg import CFG, convert_cnf_to_list, cnf_10palindrome
from implementations.my_cyk_numpy import parse
import logging


def is_matching_cfg(a: CFG, b: CFG, max_depth: int):
    a_rule_set = convert_cnf_to_list(a)
    b_rule_set = convert_cnf_to_list(b)
    index = 0
    words = (['init', ], ['init', ])
    a_enum, b_enum = Enum(a, max_depth), Enum(b, max_depth)
    while any(words):
        words = (a_enum.generate(index), b_enum.generate(index))
        logging.info(f'Checking words {words}')
        if words[0] is not None and not parse(words[0], b_rule_set):
            return False
        if words[1] is not None and not parse(words[1], a_rule_set):
            return False
        index += 1

    return True
