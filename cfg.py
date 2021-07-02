from typing import Dict, List, Union, Tuple

cfg_type = Dict[str, List[Union[Tuple, str]]]


def convert_rules_to_list(rules: cfg_type):
    new_rules = [[] for _ in rules]
    mapping = {key: index for index, key in enumerate(rules.keys())}

    for key, rule in rules.items():
        new_rules[mapping[key]] = list(map(lambda rhs_rule: convert_rhs_rule(rhs_rule, mapping), rule))

    return new_rules


def convert_rhs_rule(rule, mapping):
    if type(rule) is tuple:
        return convert_value(rule[0], mapping), convert_value(rule[1], mapping)
    return convert_value(rule, mapping)


def convert_value(value, mapping):
    if value in mapping:
        return mapping[value]
    return value


alphabet10 = ['1', '0']

cnf_10palindrome: Dict[str, List[Union[Tuple, str]]] = {
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
