from implementations.agc.enumerator import Enum
from cfg import CFG, convert_cnf_to_list
from tools import convert_cnf_to_limited_word_size, convert_to_cnf, read_gram_file
from implementations.my_cyk_memo import parse
import logging


def is_matching_cfg(a: CFG, b: CFG, max_depth: int):
    a_list = convert_cnf_to_list(a)
    b_list = convert_cnf_to_list(b)
    for depth in range(max_depth, 0, -1):
        logging.debug(f'LOOKING AT WORDS OF LENGTH {depth}')
        if not check_words_of_length(a, b, a_list, b_list, depth):
            return False

    return True


def check_words_of_length(a: CFG, b: CFG, a_list, b_list, length: int) -> bool:
    a_limited, b_limited = convert_cnf_to_limited_word_size(a, length), convert_cnf_to_limited_word_size(b, length)
    index = 0
    words = (['init', ], ['init', ])
    a_enum, b_enum = Enum(a_limited), Enum(b_limited)

    memo_a, memo_b = {}, {}

    generated_words = {None}

    while words[0] is not None or words[1] is not None:
        words = (a_enum.generate(index), b_enum.generate(index))
        if words[0] != words[1]:
            if words[0] not in generated_words and not parse(words[0], b_list, memo_b):
                return False
            else:
                generated_words.add(words[0])
            if words[1] not in generated_words and not parse(words[1], a_list, memo_a):
                return False
            else:
                generated_words.add(words[1])
        index += 1

    return True


def main():
    a_cnf = convert_to_cnf(read_gram_file(r'..\..\benchmarks\C11Grammar1.gram'))
    print(len(a_cnf.alphabet))
    b_cnf = convert_to_cnf(read_gram_file(r'..\..\benchmarks\AntlrJavaGrammar.gram'))
    import cProfile
    import pstats
    with cProfile.Profile() as pr:
        print(is_matching_cfg(a_cnf, b_cnf, 30))

    stats = pstats.Stats(pr)
    stats.dump_stats(filename='main.prof')


if __name__ == '__main__':
    logging.basicConfig(filename='main.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    main()
