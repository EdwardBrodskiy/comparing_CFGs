from implementations.agc.enumerator import Enum
from cfg import CFG, convert_cnf_to_list
from tools import convert_cnf_to_limited_word_size, convert_to_cnf, read_gram_file
from implementations.my_cyk_memo import wrapped_parse as parse_memo
from implementations.agc.main import check_words_of_length
import logging

import concurrent.futures


def check_words_of_length_threaded(a: CFG, b: CFG, length: int) -> bool:
    step = length ** 2
    a_limited, b_limited = convert_cnf_to_limited_word_size(a, length), convert_cnf_to_limited_word_size(b, length)

    a_rule_set = convert_cnf_to_list(a_limited)
    b_rule_set = convert_cnf_to_list(b_limited)

    a_enum, b_enum = Enum(a_limited, length + 2), Enum(b_limited, length + 2)

    memo_a, memo_b = {}, {}

    generated_words = {None}

    with concurrent.futures.ProcessPoolExecutor() as executor:
        threads = {}
        for start_index in range(step):
            future = executor.submit(check_match, a_rule_set, b_rule_set, a_enum, b_enum, memo_a, memo_b, generated_words,
                                     offset=start_index, step=step)
            threads[future] = start_index

        for future in concurrent.futures.as_completed(threads):
            start_index = threads[future]
            logging.debug(f'completed offset {start_index}')
            if future.result() is False:
                return False
    return True


def check_match(a_rule_set, b_rule_set, a_enum, b_enum, memo_a, memo_b, generated_words, offset=0, step=1):
    index = offset
    words = (['init', ], ['init', ])
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
        index += step
    return True


def is_matching_cfg_multiprocess(a: CFG, b: CFG, max_depth: int, method):
    threads = {}
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for depth in range(1, max_depth):
            future = executor.submit(method, a, b, depth)
            threads[future] = depth

        for future in concurrent.futures.as_completed(threads):
            depth = threads[future]
            logging.debug(f'completed depth {depth}')
            if future.result() is False:
                return False

    return True


def is_matching_cfg_multiprocess_1(a: CFG, b: CFG, max_depth: int):
    return is_matching_cfg_multiprocess(a, b, max_depth, check_words_of_length)


def is_matching_cfg_multiprocess_2(a: CFG, b: CFG, max_depth: int):
    return is_matching_cfg_multiprocess(a, b, max_depth, check_words_of_length_threaded)


def main():
    a_cnf = convert_to_cnf(read_gram_file(r'..\..\benchmarks\AntlrJavaGrammar.gram'))
    b_cnf = convert_to_cnf(read_gram_file(r'..\..\benchmarks\AntlrJavaGrammar-1-1.gram'))

    # print(is_matching_cfg_depth_respecting(a_cnf, a_cnf, 8))
    print(is_matching_cfg_multiprocess(a_cnf, b_cnf, 15))


if __name__ == '__main__':
    logging.basicConfig(filename='main.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    main()
