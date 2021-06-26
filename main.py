from nltk import *
from match_checker import is_matching_cfg as nltk_is_matching_cfg
import lark_testing as lark
import my_cyk
from timeit import timeit


def graph(results):
    column_widths = [max([len(str(round(row[column_index], 3))) for row in results.values()]) + 1 for column_index in
                     range(len(list(results.values())[0]))]
    print('name'.ljust(15), end='')
    for key, value in enumerate(range_of_depths):
        print('|', str(value).ljust(column_widths[key]), end='')
    print()
    for name, row in zip(results.keys(), results.values()):
        print(name.ljust(15), end='')
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

range_of_depths = range(7)

tests = {
    'nltk_normal': [timeit(lambda: nltk_is_matching_cfg(cfg1, cfg2, alphabet, i), number=1) for i in range_of_depths],
    'nltk_cnf_form': [timeit(lambda: nltk_is_matching_cfg(cfg1_cnf, cfg2_cnf, alphabet, i), number=1) for i in range_of_depths],
    'lark_normal': [timeit(lambda: lark.is_matching_cfg(lark.cfg, lark.cfg, alphabet, i), number=1) for i in range_of_depths],
    'lark_cyk_parser': [timeit(lambda: lark.is_matching_cfg(lark.cnf, lark.cnf, alphabet, i), number=1) for i in range_of_depths],
    'my_cyk_parser': [timeit(lambda: my_cyk.is_matching_cfg(my_cyk.cnf, my_cyk.cnf, alphabet, i), number=1) for i in range_of_depths],

}

graph(tests)
'''
name           | 0   | 1     | 2     | 3     | 4     | 5     | 6     | 7     | 8     | 9      | 10     | 11      | 12     | 13     | 14    
nltk_normal    | 0.0 | 0.002 | 0.007 | 0.023 | 0.07  | 0.247 | 0.577 | 1.533 | 4.152 | 10.413 | 26.23  | 64.567  |
nltk_cnf_form  | 0.0 | 0.002 | 0.011 | 0.045 | 0.133 | 0.357 | 0.995 | 3.031 | 7.601 | 20.09  | 50.647 | 126.634 |
lark_normal    | 0.0 | 0.001 | 0.003 | 0.01  | 0.02  | 0.055 | 0.131 | 0.317 | 0.757 | 1.644  | 3.795  | 8.821   |
lark_cyk_parser| 0.0 | 0.0   | 0.001 | 0.003 | 0.008 | 0.021 | 0.056 | 0.142 | 0.425 | 1.088  | 2.159   | 5.469   | 11.815 | 26.154 | 61.819 
my_cyk_parser  | 0.0 | 0.0   | 0.0   | 0.0   | 0.002 | 0.007 | 0.025 | 0.076 | 0.234 | 0.69   | 1.843   | 5.109   | 13.524 | 34.309 | 85.96
'''
