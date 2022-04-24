from implementations.agc.enumerator import Enum
from cfg import CFG, convert_cnf_to_list
from tools import convert_cnf_to_limited_word_size, convert_to_cnf, read_gram_file
from implementations.my_cyk_memo import wrapped_parse as parse_memo
from implementations.agc.main import check_words_of_length
import logging
import time
import math

import concurrent.futures

from multiprocessing import Process, Queue


def is_matching_cfg(a: CFG, b: CFG, max_depth: int, timeout: float = 0, is_main=None):
    if is_main is None:
        raise NotImplemented('you must create is_main=lambda: __name__ == "__main__" in the main process for multiprocessing to work')
    a_list = convert_cnf_to_list(a)
    b_list = convert_cnf_to_list(b)
    run_until = time.time() + timeout

    for depth in range(max_depth, 0, -1):
        result = check_words_of_length_threaded(a, b, a_list, b_list, depth, run_until=run_until, is_main=is_main)
        if result is False:
            return False

    return True


def is_matching_cfg_multiprocess(a: CFG, b: CFG, max_depth: int, timeout: float = 0):  # TODO: deprecated
    threads = {}
    a_list = convert_cnf_to_list(a)
    b_list = convert_cnf_to_list(b)
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
        try:
            run_until = time.time() + timeout
            for depth in range(max_depth, 0, -1):
                future = executor.submit(check_words_of_length_threaded, a, b, a_list, b_list, depth, run_until=run_until)
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


def check_words_of_length_threaded(a: CFG, b: CFG, a_list, b_list, length: int, run_until=math.inf, is_main=None) -> bool:
    step = 4
    a_limited, b_limited = convert_cnf_to_limited_word_size(a, length), convert_cnf_to_limited_word_size(b, length)

    a_enum, b_enum = Enum(a_limited), Enum(b_limited)

    memo_a, memo_b = {}, {}

    generated_words = {None}

    if is_main():
        procs = []
        q = Queue()

        for start_index in range(step):
            p = Process(target=check_match_multiprocessing, args=(q, a_list, b_list, a_enum, b_enum, memo_a, memo_b, generated_words),
                        kwargs={'offset': start_index, 'step': step, 'run_until': run_until})
            procs.append(p)

        for p in procs:
            p.start()
        for _ in procs:
            result = q.get()
            if result is False or result is TimeoutError:
                for p in procs:
                    p.terminate()
                if result is TimeoutError:
                    raise TimeoutError
                return result
    return True


def check_match_multiprocessing(q: Queue, a_rule_set, b_rule_set, a_enum, b_enum, memo_a, memo_b, generated_words, offset=0, step=1,
                                run_until=math.inf):
    index = offset
    words = (['init', ], ['init', ])
    while words[0] is not None or words[1] is not None:
        if run_until < time.time():
            q.put(TimeoutError)
        words = (a_enum.generate(index), b_enum.generate(index))

        if words[0] != words[1]:
            if words[0] not in generated_words and not parse_memo(words[0], b_rule_set, memo_b):
                q.put(False)
            if words[1] not in generated_words and not parse_memo(words[1], a_rule_set, memo_a):
                q.put(False)
        generated_words.add(words[0])
        generated_words.add(words[1])
        index += step
    q.put(True)


def main():
    a_cnf = convert_to_cnf(read_gram_file(r'..\..\benchmarks\AntlrJavaGrammar.gram'))
    b_cnf = convert_to_cnf(read_gram_file(r'..\..\benchmarks\C11Grammar1.gram'))

    is_matching_cfg(a_cnf, b_cnf, 30, timeout=60)


if __name__ == '__main__':
    logging.basicConfig(filename='main.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    main()
