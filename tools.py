from typing import Iterator, List, Set
from cfg import cfg_type, cfg_rhs, CFG, list_cnf_type, cnf_10palindrome, convert_cnf_to_list
import copy
import numpy as np
from ordered_set import OrderedSet

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


class EpsilonString(TerminalString):
    def __repr__(self):
        return 'Epsilon'


def words_of_length(length, alphabet) -> Iterator[List[str]]:
    for letter in alphabet:
        if length < 1:
            break
        elif length == 1:
            yield [letter]
        else:
            for sub_word in words_of_length(length - 1, alphabet):
                yield [letter, *sub_word]  # TODO: surely this is not the best way


def read_gram_file(name) -> (str, cfg_type):
    cfg: cfg_type = {}
    epsilon_key = '""'
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
                    if sub_rule == epsilon_key:
                        cfg[key][rule_index][sub_rule_index] = EpsilonString(sub_rule)
                    else:
                        cfg[key][rule_index][sub_rule_index] = TerminalString(sub_rule)

    return start, cfg


def convert_to_cnf(start: str, cfg: cfg_type):
    name_generator = NameGenerator(cfg)
    cnf: cfg_type = copy.deepcopy(cfg)

    # START
    cnf_start = name_generator.generate_extension(start)
    cnf[cnf_start] = [[start]]  # S0 -> S

    # DEL

    # find all nullable rules
    nullable = OrderedSet()
    found_nullable = True
    while found_nullable:
        found_nullable = False
        for key, rhs in cnf.items():
            if key not in nullable and key != cnf_start:
                has_sub_rule_consisting_of_epsilons_at_index = -1
                for rule_index, rule in enumerate(rhs):
                    rule = list(filter(lambda sr: not isinstance(sr, EpsilonString), rule))
                    if len(rule) == 0:
                        has_sub_rule_consisting_of_epsilons_at_index = rule_index
                        nullable.add(key)
                        found_nullable = True
                        continue  # TODO: assuming there is only one rule made up fully of epsilons. Maybe fix?
                    # rule may have hand some stray epsilons e.g A epsilon B which is equivalent to A B
                    cnf[key][rule_index] = rule
                    if not found_nullable:
                        if all(map(lambda sr: sr in nullable, rule)):
                            nullable.add(key)
                            found_nullable = True

                if has_sub_rule_consisting_of_epsilons_at_index != -1:
                    del cnf[key][has_sub_rule_consisting_of_epsilons_at_index]

    for key, rhs in cnf.items():
        new_sub_rules = [generate_all_non_nullable_combinations(rule, nullable) for rule in rhs]
        new_sub_rules = {sub_item for item in new_sub_rules for sub_item in item}
        rhs = {tuple(r) for r in rhs}
        cnf[key] = [list(r) for r in (rhs | new_sub_rules)]

    # TERM
    new_terminal_rules: cfg_type = {}
    terminal_to_key_mapping = {}
    for key, rhs in cnf.items():  # identify existing terminals
        if len(rhs) == 1 and len(rhs[0]) == 1 and isinstance(rhs[0][0], TerminalString):
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
    alphabet: Set[str] = set(map(lambda terminal_key: new_terminal_rules[terminal_key][0], new_terminal_rules))

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

    # UNIT
    self_pointing = set()
    for key, rhs in cnf.items():  # remove pointless loops e.g A -> A
        for rule_index, rule in enumerate(rhs):
            if len(rule) == 1 and key == rule[0]:
                self_pointing.add(key)
    for self_pointing_key in self_pointing:
        cnf[self_pointing_key] = list(filter(([self_pointing_key]).__ne__, cnf[self_pointing_key]))

    unit_rule_violations = {'rhs_violation_key': ['location_of_violation']}
    while len(unit_rule_violations):  # TODO: runs for ever seems to not be doing anything. Is this todo outdated?
        unit_rule_violations = {}
        for key, rhs in cnf.items():
            if key not in unit_rule_violations and key not in new_terminal_rules:  # TODO: new terminal rules have other rules in rhs
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

    return CFG(start=cnf_start, rules=cnf, alphabet=alphabet)


def generate_all_non_nullable_combinations(rule, nullable):
    new_rules = []
    # extract the locations of nullable non terminals
    nullables_at = list(filter(lambda sr_i: rule[sr_i] in nullable, range(len(rule))))

    no_nullables = len(nullables_at)
    for i in range(2 ** no_nullables):
        new_rule = []
        # create a unique string of ones and zeros representing a unique combination of nullables to use
        nullables_to_use = '0' * no_nullables + f'{i:b}'  # convert to binary and add preceding zeros
        nullable_index = 0
        for sub_rule_index, sub_rule in enumerate(rule):
            # if we are at a nullable skip if binary digit is 0 else add it
            if nullable_index < len(nullables_at) and sub_rule_index == nullables_at[nullable_index]:
                nullable_index += 1
                if nullables_to_use[-nullable_index] == '0':
                    continue
            new_rule.append(sub_rule)
        if new_rule:
            new_rules.append(tuple(new_rule))

    return new_rules


def is_cnf(cfg: CFG) -> bool:
    # START
    for key, rhs in cfg.rules.items():
        for rule in rhs:
            if any(map(lambda sub_rule: sub_rule == cfg.start, rule)):
                print(f'START : {key} -> {rhs}')
                return False

    # TERM
    terminals = {}
    for key, rhs in cfg.rules.items():
        for rule in rhs:
            if type(rule) is str:
                terminals[key] = rule[0][0]
            elif not all(map(lambda sub_rule: sub_rule in cfg.rules, rule)):
                print(f'TERM : {key} -> {rhs}')
                return False

    # BIN
    for key, rhs in cfg.rules.items():
        if any(map(lambda r: type(r) is not str and len(r) > 2, rhs)):
            print(f'BIN : {key} -> {rhs}')
            return False

    # DEL
    for key, rhs in cfg.rules.items():
        if key != cfg.start and any(map(lambda r: r == '""', rhs)):
            print(f'DEL : {key} -> {rhs}')
            return False

    # UNIT
    for key, rhs in cfg.rules.items():
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


def get_distance_to_terminal(rules: list_cnf_type):
    distances = np.ones([len(rules)]) * -1

    backwards_reference = {i: [] for i in range(len(rules))}
    distance_sets = [set() for _ in range(len(rules))]
    found_distance_for = set()

    for key, rhs in enumerate(rules):
        for sub_rule in rhs:
            if type(sub_rule) is str:
                if sub_rule not in backwards_reference:
                    backwards_reference[sub_rule] = [key]
                else:
                    backwards_reference[sub_rule].append(key)
            else:
                # if you are pointing to yourself this is not a productive sub_rule in the aim of getting to a terminal
                if key not in sub_rule:
                    backwards_reference[sub_rule[0]].append((key, sub_rule[1]))
                    backwards_reference[sub_rule[1]].append((key, sub_rule[0]))

    distance_sets[0] = (set(filter(lambda x: type(x) is str, backwards_reference)))

    for level in range(len(rules) - 1):
        for key in distance_sets[level]:
            for referencer in backwards_reference[key]:
                if type(referencer) is int:
                    distance_sets[level + 1].add(referencer)
                    found_distance_for.add(referencer)
                elif referencer[1] in found_distance_for and referencer[0] not in found_distance_for:
                    distance_sets[level + 1].add(referencer[0])
                    found_distance_for.add(referencer)

    for level, group in enumerate(distance_sets[1:]):
        for key in group:
            distances[key] = level

    return distances


def is_input_string_legal(chars: List[str], cfg: CFG):
    return all(map(lambda x: x in cfg.alphabet, chars))


def convert_cnf_to_limited_word_size(cnf: CFG, size: int):
    new_rules: cfg_type = {}
    new_start: str = ''
    # create all size respecting rules
    for key, rhs in cnf.rules.items():
        for i in range(size):
            new_rhs = generate_rhs_for_size(rhs, i)
            new_key = create_key(key, i)
            if len(new_rhs):  # TODO: can we stop at this size for this key?
                new_rules[new_key] = new_rhs
                if key == cnf.start:
                    new_start = new_key

    # cleanup stage removing keys with empty right-hand-sides and rules with undefined non-terminals
    changes = True  # used to track if anything was removed
    while changes:
        changes = False
        to_remove = []
        for key, rhs in new_rules.items():
            updated_rhs: cfg_rhs = []
            for i, rule in enumerate(rhs):
                # check if legal rule (terminal or has no undefined sub rules)
                if type(rule) is str or not any(map(lambda sub_rule: sub_rule not in new_rules, rule)):
                    updated_rhs.append(rule)
            if updated_rhs:
                new_rules[key] = updated_rhs
            else:
                to_remove.append(key)

            if updated_rhs != rhs:
                changes = True
        # remove keys marked empty in the prior stage
        for key in to_remove:  # TODO: we do not deal with a grammar with an empty language
            changes = True
            del new_rules[key]

    return CFG(rules=new_rules, start=new_start, alphabet=cnf.alphabet.copy())


def create_key(prev_key: str, index: int) -> str:
    return prev_key + '~SizeLimit=' + str(index)  # TODO should change keys to tuples to ensure add-ons do not interfere existing keys


def generate_rhs_for_size(rhs: cfg_rhs, size) -> cfg_rhs:
    if size == 0:
        return list(filter(lambda r: type(r) is str, rhs))
    new_rhs: cfg_rhs = []
    for rule in rhs:
        if type(rule) is not str:
            for i in range(size):
                new_rhs.append((create_key(rule[0], i), create_key(rule[1], size - 1 - i)))

    return new_rhs


def main():
    epsilon_test_cfg: cfg_type = {
        'S': [['A', 'B', 'C', TerminalString('d')]],
        'A': [['B', 'C']],
        'B': [[TerminalString('b'), 'B'], [EpsilonString('""')]],
        'C': [[TerminalString('c'), 'C'], [EpsilonString('""')]]
    }
    cnf = convert_to_cnf(*read_gram_file('.\\benchmarks\\C11Grammar1.gram'))
    result = convert_to_cnf('S', epsilon_test_cfg)
    print(result)


if __name__ == '__main__':
    main()
