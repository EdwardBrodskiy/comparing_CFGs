from implementations.agc.enumerator import Enum
from cfg import CFG, convert_cnf_to_list
from tools import convert_cnf_to_limited_word_size, convert_to_cnf, read_gram_file
from implementations.my_cyk_numpy import parse
from implementations.my_cyk_memo import wrapped_parse as parse_memo
import logging


def is_matching_cfg(a: CFG, b: CFG, max_depth: int):
    a_rule_set = convert_cnf_to_list(a)
    b_rule_set = convert_cnf_to_list(b)
    index = 0
    words = (['init', ], ['init', ])
    a_enum, b_enum = Enum(a, max_depth), Enum(b, max_depth)
    while any(words):
        words = (a_enum.generate(index), b_enum.generate(index))
        if words[0] != words[1]:
            # logging.debug(f'Checked for this length {index}.\nChecking words:\n{" ".join(words[0])}\n{" ".join(words[1])}')
            if words[0] is not None and not parse(words[0], b_rule_set):
                return False
            if words[1] is not None and not parse(words[1], a_rule_set):
                return False
        index += 1
    logging.debug(f'finished checking {index} words')
    return True


def is_matching_cfg_depth_respecting(a: CFG, b: CFG, max_depth: int):
    WORD_COUNT = 0
    CHECK_COUNT = 0
    for depth in range(max_depth, 0, -1):
        logging.debug(f'LOOKING AT WORDS OF LENGTH {depth}')
        a_limited, b_limited = convert_cnf_to_limited_word_size(a, depth), convert_cnf_to_limited_word_size(b, depth)

        a_rule_set = convert_cnf_to_list(a_limited)
        b_rule_set = convert_cnf_to_list(b_limited)
        index = 0
        words = (['init', ], ['init', ])
        a_enum, b_enum = Enum(a_limited, max_depth), Enum(b_limited, max_depth)
        while any(words):
            words = (a_enum.generate(index), b_enum.generate(index))

            if words[0] != words[1]:
                # logging.debug(f'Checked for this length {index}.\nChecking words:\n{" ".join(words[0])}\n{" ".join(words[1])}')
                if words[0] is not None and not parse(words[0], b_rule_set):
                    return False
                if words[1] is not None and not parse(words[1], a_rule_set):
                    return False
                CHECK_COUNT += 1
            index += 1
            WORD_COUNT += 1

    logging.info(f'non-memo: finished checking {CHECK_COUNT} words and looking at a total of {WORD_COUNT}')
    return True


def is_matching_cfg_depth_respecting_memo(a: CFG, b: CFG, max_depth: int):
    for depth in range(max_depth, 0, -1):
        logging.debug(f'LOOKING AT WORDS OF LENGTH {depth}')
        if not check_words_of_length(a, b, depth):
            return False

    return True


def check_words_of_length(a: CFG, b: CFG, length: int) -> bool:
    a_limited, b_limited = convert_cnf_to_limited_word_size(a, length), convert_cnf_to_limited_word_size(b, length)

    a_rule_set = convert_cnf_to_list(a_limited)
    b_rule_set = convert_cnf_to_list(b_limited)
    index = 0
    words = (['init', ], ['init', ])
    a_enum, b_enum = Enum(a_limited, length + 2), Enum(b_limited, length + 2)

    memo_a, memo_b = {}, {}

    generated_words = {None}

    while words[0] is not None or words[1] is not None:
        words = (a_enum.generate(index), b_enum.generate(index))
        if words[0] != words[1]:
            # logging.debug(f'Checked for this length {index}.\nChecking words:\n{" ".join(words[0])}\n{" ".join(words[1])}')
            if words[0] not in generated_words and not parse_memo(words[0], b_rule_set, memo_b):
                return False
            if words[1] not in generated_words and not parse_memo(words[1], a_rule_set, memo_a):
                return False
        generated_words.add(words[0])
        generated_words.add(words[1])
        index += 1
    return True


def main():
    a_cnf = convert_to_cnf(read_gram_file(r'..\..\benchmarks\AntlrJavaGrammar.gram'))
    print(len(a_cnf.alphabet))
    b_cnf = convert_to_cnf(read_gram_file(r'..\..\benchmarks\AntlrJavaGrammar-1-1.gram'))

    print(is_matching_cfg_depth_respecting(a_cnf, a_cnf, 8))


if __name__ == '__main__':
    logging.basicConfig(filename='main.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    main()
