from lark import Lark, ParseError
from tools import words_of_length


def is_accepted(lark_cfg: Lark, word_to_parse):
    try:
        lark_cfg.parse(word_to_parse)
        return True
    except ParseError:
        return False


def is_matching_cfg(a: Lark, b: Lark, alphabet, max_depth: int):
    for depth in range(max_depth):
        for word in words_of_length(depth, alphabet):
            word = ''.join(word)
            if is_accepted(a, word) != is_accepted(b, word):
                return False
    return True


def is_matching_cfg_wrapper_10palindrome_earley(max_depth):
    return is_matching_cfg(cfg_10palindrome, cfg_10palindrome, alph, max_depth)


def is_matching_cfg_wrapper_10palindrome_cyk(max_depth):
    return is_matching_cfg(cnf_10palindrome, cnf_10palindrome, alph, max_depth)


alph = ['1', '0']

grammar = '''
start: one start one | zero start zero | one | zero
one: "1"
zero: "0"
'''

chomsky_grammar = '''
start: one alterone | zero alterzero | one | zero 
base: one alterone | zero alterzero | one | zero 
alterone: base one
alterzero: base zero
one: "1"
zero: "0"
'''

cfg_10palindrome = Lark(grammar, start='start')
cnf_10palindrome = Lark(chomsky_grammar, parser='cyk', start='start')
