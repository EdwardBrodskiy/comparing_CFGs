from implementations.agc.enumerator import Enum
from cfg import CFG, convert_cnf_to_list
from tools import convert_cnf_to_limited_word_size, convert_to_cnf, read_gram_file
from implementations.my_cyk_memo import wrapped_parse as parse_memo
from implementations.agc.main import check_words_of_length
import logging
import time
import math

import concurrent.futures

import threading
import sys
import _thread as thread


def exit_after(s):
    def outer(fn):
        def inner(*args, **kwargs):
            timer = threading.Timer(s, quit_function)
            timer.start()
            try:
                result = fn(*args, **kwargs)
            except KeyboardInterrupt:
                result = None
            finally:
                timer.cancel()
            return result

        return inner

    return outer


def quit_function():
    sys.stderr.flush()  # Python 3 stderr is likely buffered.
    thread.interrupt_main()  # raises KeyboardInterrupt


def check_words_of_length_threaded(a: CFG, b: CFG, a_list, b_list, length: int, run_until=math.inf) -> bool:
    # print(f'starting checking words of length {length}')
    timed_out = False
    step = 16
    a_limited, b_limited = convert_cnf_to_limited_word_size(a, length), convert_cnf_to_limited_word_size(b, length)

    a_enum, b_enum = Enum(a_limited, length + 2), Enum(b_limited, length + 2)

    memo_a, memo_b = {}, {}

    generated_words = {None}

    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        threads = {}

        try:
            for start_index in range(step):
                future = executor.submit(check_match_multiprocessing, a_list, b_list, a_enum, b_enum, memo_a, memo_b,
                                         generated_words,
                                         offset=start_index, step=step, run_until=run_until)
                threads[future] = start_index
            for future in concurrent.futures.as_completed(threads):
                start_index = threads[future]
                logging.debug(f'completed offset {start_index}')
                if future.result() is False:
                    executor.shutdown(wait=False)
                    return False
        except TimeoutError:
            # print(f'{length} has timed out')
            for future in threads:
                if not future.done():
                    future.cancel()
            executor.shutdown(wait=False)

            raise TimeoutError

    return True


def check_match_multiprocessing(a_rule_set, b_rule_set, a_enum, b_enum, memo_a, memo_b, generated_words, offset=0, step=1,
                                run_until=math.inf):
    index = offset
    words = (['init', ], ['init', ])
    while words[0] is not None or words[1] is not None:
        if run_until < time.time():
            print(f'TMO {index} ')
            raise TimeoutError
        words = (a_enum.generate(index), b_enum.generate(index))
        print(f'check {index}', end=' ')
        if words[0] != words[1]:
            # logging.debug(f'Checked for this length {index}.\nChecking words:\n{" ".join(words[0])}\n{" ".join(words[1])}')
            print('check')
            if words[0] not in generated_words and not parse_memo(words[0], b_rule_set, memo_b):
                print('diff')
                return False
            if words[1] not in generated_words and not parse_memo(words[1], a_rule_set, memo_a):
                print('diff')
                return False
        generated_words.add(words[0])
        generated_words.add(words[1])
        index += step
    return True


def is_matching_cfg_multiprocess(a: CFG, b: CFG, max_depth: int, method, timeout: float = 0):
    threads = {}
    a_list = convert_cnf_to_list(a)
    b_list = convert_cnf_to_list(b)
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
        try:
            run_until = time.time() + timeout
            for depth in range(max_depth, 0, -1):
                future = executor.submit(method, a, b, a_list, b_list, depth, run_until=run_until)
                threads[future] = depth
            for future in concurrent.futures.as_completed(threads):
                depth = threads[future]
                logging.debug(f'completed depth {depth}')
                if future.result() is False:
                    executor.shutdown(wait=False)
                    return False
        except TimeoutError:
            for future in threads:
                if not future.done():
                    future.set_exception(TimeoutError)
            executor.shutdown()
            return None
    return True


def is_matching_cfg(a: CFG, b: CFG, max_depth: int, method, timeout: float = 0):
    threads = {}

    run_until = time.time() + timeout
    try:
        for depth in range(max_depth, 0, -1):
            result = method(a, b, depth, run_until=run_until)
            if result is False:
                return False
    except TimeoutError:
        return None
    return True


def is_matching_cfg_multiprocess_1(a: CFG, b: CFG, max_depth: int, timeout=math.inf):
    return is_matching_cfg_multiprocess(a, b, max_depth, check_words_of_length, timeout=timeout)


def is_matching_cfg_multiprocess_2(a: CFG, b: CFG, max_depth: int, timeout=math.inf):
    return is_matching_cfg_multiprocess(a, b, max_depth, check_words_of_length_threaded, timeout=timeout)


def main():
    a_cnf = convert_to_cnf(read_gram_file(r'..\..\benchmarks\AntlrJavaGrammar.gram'))
    b_cnf = convert_to_cnf(read_gram_file(r'..\..\benchmarks\C11Grammar1.gram'))

    # print(is_matching_cfg_depth_respecting(a_cnf, a_cnf, 8))
    print(is_matching_cfg_multiprocess_2(a_cnf, b_cnf, 30, timeout=60))


if __name__ == '__main__':
    logging.basicConfig(filename='main.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    main()
