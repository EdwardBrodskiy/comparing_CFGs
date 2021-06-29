from timeit import timeit
import csv
from typing import Dict, Union, List

from implementations import my_cyk, nltk_testing as nltk, lark_testing as lark

timeout: float = 60  # time until a given test times out
timeout_key: str = ''

max_depth: int = 5  # to what length to run the tests

re_runs: int = 5  # how many times to run test

re_build_table: bool = False  # re use old results or work from scratch

tests = {
    '10palindrome': {
        'my_cyk': my_cyk.is_matching_cfg_wrapper_10palindrome,
        'lark_earley': lark.is_matching_cfg_wrapper_10palindrome_earley,
        'lark_cyk': lark.is_matching_cfg_wrapper_10palindrome_cyk,
        'nltk_recursive_decent': nltk.is_matching_cfg_wrapper_recursive_decent
    }
}

for test_name, test in tests.items():

    # Load past results

    past_results: Dict[str, List[str]] = {}
    past_header: List[str] = []
    if not re_build_table:
        try:
            with open(f'{test_name}_results.csv', 'r') as file:
                csv_reader = csv.reader(file)
                past_header = next(csv_reader)
                for name, *results in csv_reader:
                    past_results[name] = results
        except FileNotFoundError:
            re_build_table = True

    results: Dict[str, List[Union[float, str]]] = {}

    # Merge past results into new table

    if not re_build_table:
        for name in test:
            if name not in past_results:
                past_results[name] = []

            if len(past_results[name]) >= max_depth:
                results[name] = past_results[name]
            else:
                results[name] = [0 for _ in range(max_depth)]
                for i, past_result in enumerate(past_results[name]):
                    try:
                        past_result = float(past_result)
                    except ValueError:
                        pass
                    results[name][i] = past_result
    else:
        results = {name: [0 for _ in range(max_depth)] for name in test}

    # run the tests

    print(f'Test cycle for {test_name}\n' + ''.join(list(map(lambda x: str(x).rjust(4), range(1, re_runs + 1)))))
    for run_index in range(re_runs):  # this is done instead of changing the number on timeit to spread out the tests
        for depth in range(1, max_depth + 1):
            for name, approach in test.items():
                if re_build_table or len(past_results[name]) < depth:  # do we need this value
                    if results[name][depth - 1] == timeout_key:  # skip if already timed out on prior runs
                        continue

                    # check if the previous length went over the threshold if so time out
                    if timeout and depth > 1 and (results[name][depth - 2] == timeout_key
                                                  or results[name][depth - 2] / (run_index + 1) > timeout):
                        results[name][depth - 1] = timeout_key
                    else:  # Actually run the test
                        result = timeit(lambda: approach(depth), number=1)
                        results[name][depth - 1] += result
                        if run_index + 1 == re_runs:
                            results[name][depth - 1] = round(results[name][depth - 1] / re_runs, 3)
        print('---|', end='')

    # Save the new table

    saved = False
    while not saved:
        try:
            with open(f'{test_name}_results.csv', 'w', newline='') as file:
                csv_writer = csv.writer(file)

                csv_writer.writerow(max(['name', *list(range(1, max_depth + 1))], past_header, key=lambda x: len(x)))

                for name, results in results.items():
                    csv_writer.writerow([name, *results])
            saved = True
        except PermissionError:
            input('Permission Denied PRESS ENTER TO TRY AGAIN')
