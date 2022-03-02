from implementations.agc.agc_enum import Enum
from cfg import CFG, convert_cnf_to_list, cnf_10palindrome
from tools import convert_cnf_to_limited_word_size
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


def is_matching_cfg_depth_respecting(a: CFG, b: CFG, max_depth: int):
    for depth in range(1, max_depth):
        a_limited, b_limited = convert_cnf_to_limited_word_size(a, depth), convert_cnf_to_limited_word_size(b, depth)

        a_rule_set = convert_cnf_to_list(a_limited)
        b_rule_set = convert_cnf_to_list(b_limited)
        index = 0
        words = (['init', ], ['init', ])
        a_enum, b_enum = Enum(a_limited, max_depth), Enum(b_limited, max_depth)
        while any(words):
            words = (a_enum.generate(index), b_enum.generate(index))
            logging.info(f'Checking words {words}')
            if words[0] is not None and not parse(words[0], b_rule_set):
                return False
            if words[1] is not None and not parse(words[1], a_rule_set):
                return False
            index += 1

    return True
