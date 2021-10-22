from nltk import *


def words_of_depth(depth, alphabet):
    for letter in alphabet:
        if depth == 0:
            yield letter
        else:
            for sub_word in words_of_depth(depth - 1, alphabet):
                yield [letter, *sub_word]


def is_matching_cfg(a, b, alphabet, max_depth: int, parser=RecursiveDescentParser):
    parser_a = parser(a)

    parser_b = parser(b)
    for depth in range(max_depth + 1):
        for word in words_of_depth(depth, alphabet):

            if (len(list(parser_a.parse(word))) == 0) != (len(list(parser_b.parse(word))) == 0):
                print("CFG's don't for word_to_parse", ''.join(word))
                return False
    return True


def is_matching_cfg_wrapper_recursive_decent(max_depth):
    return is_matching_cfg(cfg_10palindrome, cfg_10palindrome, alph, max_depth)


alph = ['0', '1']

grammar1 = """
S -> X S X | Y S Y | X | Y
X -> '0'
Y -> '1'
"""

cfg_10palindrome = CFG.fromstring(grammar1)

# cnf_10palindrome = cfg_10palindrome.chomsky_normal_form()
