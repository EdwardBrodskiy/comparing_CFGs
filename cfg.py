from typing import Dict, List, Union, Tuple, Callable, Set
from dataclasses import dataclass

cfg_rhs = List[Union[Tuple, str, List]]

cfg_type = Dict[str, cfg_rhs]

list_cnf_type = List[List[Union[Tuple[int, int], str]]]

@dataclass
class CFG:
    rules: cfg_type
    alphabet: Set[str]
    start: str = 'S'


type_is_matching_cfg = Callable[[CFG, CFG, int], bool]


def convert_cnf_to_list(cnf: CFG) -> list_cnf_type:
    new_rules = [[] for _ in cnf.rules]

    keys = list(cnf.rules.keys())
    keys[keys.index(cnf.start)], keys[0] = keys[0], cnf.start

    mapping = {key: index for index, key in enumerate(keys)}

    for key, rhs in cnf.rules.items():
        new_rules[mapping[key]] = list(map(lambda rule: convert_rhs_rule(rule, mapping), rhs))

    return new_rules


def convert_rhs_rule(rule, mapping):
    if type(rule) is tuple or type(rule) is list:
        return convert_value(rule[0], mapping), convert_value(rule[1], mapping)
    return convert_value(rule, mapping)


def convert_value(value, mapping):
    if value in mapping:
        return mapping[value]
    return value


cnf_10palindrome = CFG(
    rules={
        # start
        'S': [('X', 'A'), ('Y', 'B'), '1', '0'],
        # base
        'D': [('X', 'A'), ('Y', 'B'), '1', '0'],
        # alterone
        'A': [('D', 'X')],
        # alterzero
        'B': [('D', 'Y')],
        # one
        'X': ['1'],
        # zero
        'Y': ['0']
    },
    alphabet={'1', '0'}
)
