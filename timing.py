from timeit import timeit
import csv

from my_cyk import is_matching_cfg_wrapper_10palindrome

timeout = 100  # time until a test times out #TODO: implement
max_depth = 11  # to what depth to run the tests
re_runs = 2  # how many times to run test
re_build_table = True  # re use old results or work from scratch

tests = {
    '10palindrome': {
        'my_cyk': is_matching_cfg_wrapper_10palindrome
    }
}

for test_name, test in tests.items():
    past_results = {}

    if not re_build_table:
        try:
            with open(f'{test_name}_results.csv', 'r') as file:
                csv_reader = csv.reader(file)
                header = next(csv_reader)
                for name, *results in csv_reader:
                    past_results[name] = results
        except FileNotFoundError:
            re_build_table = True

    results = {}

    if not re_build_table:
        for name in test:
            if name not in past_results:
                past_results[name] = []

            if len(past_results[name]) >= max_depth:
                results[name] = past_results[name]
            else:
                results[name] = [0 for _ in range(max_depth)]
                for i, past_result in enumerate(past_results[name]):
                    results[name][i] = past_result
    else:
        results = {name: [0 for _ in range(max_depth)] for name in test}

    for run_index in range(re_runs):  # this is done instead of changing the number on timeit to spread out the tests
        for depth in range(1, max_depth + 1):
            for name, approach in test.items():
                if re_build_table or len(past_results[name]) < depth:
                    result = timeit(lambda: approach(depth), number=1)
                    results[name][depth - 1] += result
                    if run_index + 1 == re_runs:
                        results[name][depth - 1] = round(results[name][depth - 1] / re_runs, 3)

    combined_results = results.copy()

    with open(f'{test_name}_results.csv', 'w', newline='') as file:
        csv_writer = csv.writer(file)

        csv_writer.writerow(['name', *list(range(1, max_depth + 1))])

        for name, results in combined_results.items():
            csv_writer.writerow([name, *results])
