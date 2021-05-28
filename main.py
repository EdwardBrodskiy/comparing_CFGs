from nltk import *
from match_checker import is_matching_cfg
from timeit import timeit


def graph(results):
    column_widths = [max([len(str(round(row[column_index], 3))) for row in results.values()]) + 1 for column_index in
                     range(len(results['normal']))]
    print('name'.ljust(10), end='')
    for key, value in enumerate(range_of_depths):
        print('|', str(value).ljust(column_widths[key]), end='')
    print()
    for name, row in zip(results.keys(), results.values()):
        print(name.ljust(10), end='')
        for key, result in enumerate(row):
            print('|', str(round(result, 3)).ljust(column_widths[key]), end='')
        print()


alphabet = ['0', '1']

grammar1 = """
S -> X S X | Y S Y | X | Y
X -> '0'
Y -> '1'
"""

grammar2 = """
S -> X S X | Y S Y | X | Y
X -> '0'
Y -> '1'
"""

cfg1 = CFG.fromstring(grammar1)

cfg2 = CFG.fromstring(grammar2)

cfg1_cnf = cfg1.chomsky_normal_form()
cfg2_cnf = cfg2.chomsky_normal_form()

range_of_depths = range(4)

tests = {
    'normal': [timeit(lambda: is_matching_cfg(cfg1, cfg2, alphabet, i), number=1) for i in range_of_depths],
    'cnf_form': [timeit(lambda: is_matching_cfg(cfg1_cnf, cfg2_cnf, alphabet, i), number=1) for i in range_of_depths],
}

graph(tests)
print(is_matching_cfg(cfg1, cfg2, alphabet, 5))
