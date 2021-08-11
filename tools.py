from typing import Iterator, List


class TerminalString(str):
    pass


def main():
    cfg = read_gram_file('benchmarks\\AntlrJavaGrammar-1-1.gram')
    print(type(cfg['interfaceBodyDeclaration'][1][0]))


def words_of_length(length, alphabet) -> Iterator[List[str]]:
    for letter in alphabet:
        if length < 1:
            break
        elif length == 1:
            yield letter
        else:
            for sub_word in words_of_length(length - 1, alphabet):
                yield [letter, *sub_word]  # TODO: surely this is not the best way


def read_gram_file(name):
    cfg = {}
    with open(name) as file:
        for line in file:
            key, rhs = line.split(' -> ')  # TODO: should use a safe split in the case that ' -> ' is in the rhs
            cfg[key] = []
            rhs = rhs.split(' | ')
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

    return cfg


if __name__ == '__main__':
    main()
