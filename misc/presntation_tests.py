from cfg import CFG
from tools import read_gram_file, convert_to_cnf
from implementations.agc.main import is_matching_cfg


def main():
    background_grammar_a = read_gram_file(r'.\grammar_a.gram')
    background_grammar_b = read_gram_file(r'.\grammar_b.gram')

    a_cnf = convert_to_cnf(background_grammar_a)
    b_cnf = convert_to_cnf(background_grammar_b)
    print(a_cnf.rules)
    print(b_cnf.rules)

    print(is_matching_cfg(a_cnf, b_cnf, 7))


if __name__ == '__main__':
    main()
