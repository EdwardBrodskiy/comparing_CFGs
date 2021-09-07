from typing import Dict, List, Union, Tuple, Callable

cfg_rhs = List[Union[Tuple, str, List]]

cfg_type = Dict[str, cfg_rhs]

type_is_matching_cfg = Callable[[cfg_type, cfg_type, List[str], int], bool]


def convert_cnf_to_list(cnf: cfg_type):
    new_rules = [[] for _ in cnf]
    mapping = {key: index for index, key in enumerate(cnf.keys())}

    for key, rhs in cnf.items():
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


alphabet10 = ['1', '0']

cnf_10palindrome: cfg_type = {
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
}
