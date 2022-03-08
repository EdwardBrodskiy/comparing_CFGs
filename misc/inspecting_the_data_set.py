import numpy as np
import os
from utils import load_gram_files
from tools import convert_to_cnf
import implementations.agc.main as agc


def main():
    amount = 25
    path = os.path.join('..', 'benchmarks')
    number_of_files = len(list(filter(lambda f: '.gram' == f[-5:], os.listdir(path))))
    results = np.zeros((number_of_files, number_of_files), dtype=np.int8)
    mapping = []
    for a_index, a_iter in enumerate(load_gram_files(amount=amount, path=path)):
        a_name, a_cfg = a_iter
        a_cnf = convert_to_cnf(*a_cfg)
        for b_index, b_iter in enumerate(load_gram_files(amount=amount, path=path)):
            b_name, b_cfg = b_iter
            b_cnf = convert_to_cnf(*b_cfg)
            results[a_index, b_index] = agc.is_matching_cfg_depth_respecting(a_cnf, b_cnf, 6)
            if results[a_index, b_index]:
                print('.', end='')
            else:
                print('X', end='')

        print(' ', round((a_index + 1) / number_of_files * 100, 2), '%')
        np.savetxt("temp.csv", results, delimiter=",")
        mapping.append(a_name)

    print(results)
    print(mapping)
    success = False
    while not success:  # we don't want any errors to cause a crash as we don't want to loose the data
        try:
            np.savetxt("all_comps.csv", results, delimiter=",")
            success = True
        except:
            input('Something went wrong')


if __name__ == '__main__':
    main()
