from typing import Iterator, List
from cfg import cfg_type
import copy

'''
CFG structure note to self:

<key> -> <rhs>

<rhs> == <rule> | <rule> | <rule> ...

<rule> == <sub_rule> <sub_rule> ...
'''


class TerminalString(str):
    def __repr__(self):
        string = super().__repr__().strip('\'')
        return f'Terminal:"{string}"'


def main():
    start, cfg = read_gram_file('benchmarks\\C11Grammar1-1-1.gram')
    cnf_start, cnf = convert_to_cnf(start, cfg)
    print(is_cnf(cnf_start, cnf))
    print(len(cfg))
    print(len(cnf))


def words_of_length(length, alphabet) -> Iterator[List[str]]:
    for letter in alphabet:
        if length < 1:
            break
        elif length == 1:
            yield letter
        else:
            for sub_word in words_of_length(length - 1, alphabet):
                yield [letter, *sub_word]  # TODO: surely this is not the best way


def read_gram_file(name) -> (str, cfg_type):
    cfg: cfg_type = {}
    first = True
    start = ''
    with open(name) as file:
        for line in file:
            key, *rhs = line.split(' -> ')
            rhs = ' -> '.join(rhs)  # undo any unintended splitting due to ' -> ' appearing later on
            if first:
                start = key
                first = False

            cfg[key] = []
            rhs = rhs.split(' | ')  # TODO: this may cause errors if there is a terminal "\' | \'"
            for rule in rhs:
                rule = rule.strip()
                sub_rules = rule.split()
                for index, sub_rule in enumerate(sub_rules):
                    if sub_rule[0] == '\'' and sub_rule[-1] == '\'':
                        sub_rules[index] = sub_rule[1: -1]

                cfg[key].append(sub_rules)

    for key, rhs in cfg.items():
        for rule_index, rule in enumerate(rhs):
            for sub_rule_index, sub_rule in enumerate(rule):
                if sub_rule not in cfg:
                    cfg[key][rule_index][sub_rule_index] = TerminalString(sub_rule)

    return start, cfg


def convert_to_cnf(start: str, cfg: cfg_type):
    name_generator = NameGenerator(cfg)
    cnf: cfg_type = copy.deepcopy(cfg)

    # START
    cnf_start = name_generator.generate_extension(start)
    cnf[cnf_start] = [[start]]  # S0 -> S

    # TERM
    new_terminal_rules: cfg_type = {}
    terminal_to_key_mapping = {}
    for key, rhs in cnf.items():  # identify existing terminals
        if len(rhs) == 1 and len(rhs[0]) == 1 and type(rhs[0][0]) is TerminalString:
            new_terminal_rules[key] = [str(rhs[0][0])]
            terminal_to_key_mapping[rhs[0][0]] = key

    for key, rhs in cnf.items():  # create new terminals
        for rule in rhs:
            for sub_rule in rule:
                if type(sub_rule) is TerminalString and sub_rule not in terminal_to_key_mapping:
                    new_terminal_key = name_generator.generate_key(sub_rule)
                    new_terminal_rules[new_terminal_key] = [str(sub_rule)]
                    terminal_to_key_mapping[sub_rule] = new_terminal_key

    for key, rhs in cnf.items():  # replace strings with terminals
        for rule_index, rule in enumerate(rhs):
            for sub_rule_index, sub_rule in enumerate(rule):
                if type(sub_rule) is TerminalString:
                    cnf[key][rule_index][sub_rule_index] = terminal_to_key_mapping[str(sub_rule)]
    cnf = cnf | new_terminal_rules

    # BIN
    new_extension_rules = {}
    for key, rhs in cnf.items():
        for rule_index, rule in enumerate(rhs):
            if type(rule) is not str and len(rule) > 2:
                extension_rule_key = name_generator.generate_extension(key)
                cnf[key][rule_index] = [rule[0], extension_rule_key]

                for i in range(1, len(rule) - 2):
                    next_extension_rule_key = name_generator.generate_extension(key)
                    new_extension_rules[extension_rule_key] = [[rule[i], next_extension_rule_key]]
                    extension_rule_key = next_extension_rule_key
                new_extension_rules[extension_rule_key] = [rule[-2:]]
    cnf = cnf | new_extension_rules

    # DEL
    '''
    I think we are ok to skip this step for now as what is meant to be an empty string is being treated as
    "" hence we don't have empty strings.
    '''

    # UNIT
    self_pointing = set()
    for key, rhs in cnf.items():  # remove pointless loops e.g A -> A
        for rule_index, rule in enumerate(rhs):
            if len(rule) == 1 and key == rule[0]:
                self_pointing.add(key)
    for self_pointing_key in self_pointing:
        cnf[self_pointing_key] = list(filter(([self_pointing_key]).__ne__, cnf[self_pointing_key]))

    unit_rule_violations = {'rhs_violation_key': ['location_of_violation']}
    while len(unit_rule_violations):  # TODO: runs for ever seems to not be doing anything
        unit_rule_violations = {}
        for key, rhs in cnf.items():
            if key not in unit_rule_violations and key not in new_terminal_rules:
                for rule in rhs:
                    violating_key = rule[0]
                    if type(rule) is not str and len(rule) == 1:
                        if violating_key not in unit_rule_violations:
                            unit_rule_violations[violating_key] = []
                        unit_rule_violations[violating_key].append(key)

        for violating_key, violation_locations in unit_rule_violations.items():
            for key in violation_locations:
                cnf[key].remove([violating_key])
                cnf[key] += cnf[violating_key]

    return cnf_start, cnf


def is_cnf(start: str, cfg: cfg_type) -> bool:
    # START
    for key, rhs in cfg.items():
        for rule in rhs:
            if any(map(lambda sub_rule: sub_rule == start, rule)):
                print(f'START : {key} -> {rhs}')
                return False

    # TERM
    terminals = {}
    for key, rhs in cfg.items():
        for rule in rhs:
            if type(rule) is str:
                terminals[key] = rule[0][0]
            elif not all(map(lambda sub_rule: sub_rule in cfg, rule)):
                print(f'TERM : {key} -> {rhs}')
                return False

    # BIN
    for key, rhs in cfg.items():
        if any(map(lambda r: type(r) is not str and len(r) > 2, rhs)):
            print(f'BIN : {key} -> {rhs}')
            return False

    # DEL
    '''
    I think we are ok to skip this step for now as what is meant to be an empty string is being treated as
    "" hence we don't have empty strings.
    '''

    # UNIT
    for key, rhs in cfg.items():
        for rule in rhs:
            if type(rule) is not str and len(rule) == 1:
                print(f'UNIT : {key} -> {rule}')
                print(terminals)
                return False
    return True


class NameGenerator:
    def __init__(self, cfg: dict, append_div='_'):
        self.cfg_name_count = {key: 0 for key in cfg.keys()}
        self.append_div = append_div

    def generate_extension(self, parent_key):
        while True:
            new_key = parent_key + self.append_div + str(self.cfg_name_count[parent_key])
            self.cfg_name_count[parent_key] += 1
            if new_key not in self.cfg_name_count:
                self.cfg_name_count[new_key] = 0
                return new_key

    def generate_key(self, name):
        modifier_counter = 0
        modifier = ''
        while True:
            new_key = self.append_div + name + self.append_div + modifier
            if new_key not in self.cfg_name_count:
                self.cfg_name_count[new_key] = 0
                return new_key
            modifier = str(modifier_counter)
            modifier_counter += 1


if __name__ == '__main__':
    main()
