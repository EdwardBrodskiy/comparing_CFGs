from nltk import *
from match_checker import is_matching_cfg as nltk_is_matching_cfg
import lark_testing as lark
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

range_of_depths = range(12)

tests = {
    'nltk_normal': [timeit(lambda: nltk_is_matching_cfg(cfg1, cfg2, alphabet, i), number=1) for i in range_of_depths],
    'nltk_cnf_form': [timeit(lambda: nltk_is_matching_cfg(cfg1_cnf, cfg2_cnf, alphabet, i), number=1) for i in range_of_depths],
    'lark_normal': [timeit(lambda: lark.is_matching_cfg(lark.cfg, lark.cfg, alphabet, i), number=1) for i in range_of_depths],
    'lark_cyk_parser': [timeit(lambda: lark.is_matching_cfg(lark.cnf, lark.cnf, alphabet, i), number=1) for i in range_of_depths],

}

graph(tests)
'''
name           | 0   | 1     | 2     | 3     | 4     | 5     | 6     | 7     | 8     | 9      | 10     | 11      
nltk_normal    | 0.0 | 0.002 | 0.008 | 0.028 | 0.087 | 0.254 | 0.727 | 2.178 | 4.676 | 12.806 | 28.031 | 67.357  
nltk_cnf_form  | 0.0 | 0.002 | 0.008 | 0.033 | 0.133 | 0.391 | 1.125 | 3.013 | 7.923 | 20.349 | 51.167 | 127.663 
lark_normal    | 0.0 | 0.001 | 0.002 | 0.009 | 0.02  | 0.06  | 0.145 | 0.319 | 0.752 | 1.748  | 3.932  | 8.762   
lark_cyk_parser| 0.0 | 0.001 | 0.001 | 0.003 | 0.008 | 0.021 | 0.069 | 0.159 | 0.383 | 0.99   | 2.435  | 5.408 
'''
