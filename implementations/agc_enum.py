from cfg import CFG, cfg_rhs, cnf_10palindrome, convert_cnf_to_list
from tools import words_of_length, read_gram_file, convert_to_cnf, convert_cnf_to_limited_word_size
from typing import Union, Tuple
from math import prod, floor, sqrt, ceil
from implementations.my_cyk_numpy import parse

from misc.recursion_decorator import recviz

memo = {}


def memory(f):
    def helper(*args, **kwargs):
        key = (f.__name__, args)
        if key not in memo:
            memo[key] = f(*args, **kwargs)
        return memo[key]

    return helper


@recviz
def enum(root: Tuple[str, ...], index: int, depth=100, cfg: CFG = None) -> Union[Tuple[str, ...], None]:
    if len(root) == 1:
        key: str = root[0]
        """
        For a terminal a belonging to a grammar, Enum[a] is defined as {0 → leaf (a)}.
        """
        if key in cfg.alphabet:
            if index == 0:
                return tuple((key,))
            return None

        return enum(*choose(key, index, depth=depth - 1, cfg=cfg), depth=depth - 1, cfg=cfg)

    sub_enums = []  # TODO: this is not how it is done in the paper
    if len(root) != 2:  # root is expected to be size to as all expansions of a CNF are size 2 or 1
        raise Exception('Ensure grammar is in CNF')
    x_rhs, y_rhs = get_no_trees((root[0],), depth, cfg=cfg), get_no_trees((root[1],), depth, cfg=cfg)
    if x_rhs * y_rhs <= index:
        return None
    cartesian_expansion_coords = map_to_space(index, x_rhs, y_rhs)
    print(f'{index=} {x_rhs=} {y_rhs=} {cartesian_expansion_coords=}')
    for m, sub_rule in enumerate(root):
        sub_enums.append(enum((sub_rule,), cartesian_expansion_coords[m], depth=depth, cfg=cfg))
    if not all(sub_enums):
        return None
    return tuple(item for sublist in sub_enums for item in sublist)


def choose(key: str, index: int, depth: int, cfg: CFG = None) -> Tuple[Tuple[str, ...], int]:
    # '#t' is used to denote the number of parse trees belonging to the right-hand-sides calculated by function 'get_no_trees'

    # extract all sentential forms which are the rhs of the given key
    # NOTE: in ascending order of #t (sorted prior)
    sentential_forms = list(map(lambda rule: (rule,) if type(rule) is str else rule, cfg.rules[key]))
    n = len(sentential_forms)

    # let b0 = 0, and b1, · · · , bn = #t(α0), · · · , #t(αn−1)
    trees: Tuple[int, ...] = (0, *list(map(lambda sentential_form: get_no_trees(tuple(sentential_form), depth, cfg=cfg), sentential_forms)))

    # wrap helper to better fit original definition
    def i(bound):
        return helper_index(bound, n, trees)

    # let k be such that 0 ≤ k ≤ n − 1 and i[k] ≤ index < i[k]+1
    k = 0
    while k < n and i(k) <= index:
        k += 1
    k -= 1

    # let q = floor((index − i[k])/(n − k)) and r = (index − i[k])%(n − k)
    q = (index - i(k)) // (n - k)
    r = (index - i(k)) % (n - k)

    return tuple(sentential_forms[k + r]), trees[k] + q


def helper_index(m: int, n: int, b: Tuple[int]) -> int:
    return b[m] * (n - m + 1) + sum(b[: m])


def sort_cfg_tree_wise(cfg: CFG, depth):
    for key, rhs in cfg.rules.items():
        cfg.rules[key] = sorted(rhs,
                                key=lambda rule: get_no_trees((rule,), depth, cfg=cfg) if type(rule) is str else get_no_trees(tuple(rule),
                                                                                                                              depth,
                                                                                                                              cfg=cfg))


@memory
def get_no_trees(root: Tuple[str, ...], max_depth: int, cfg: CFG = None) -> int:
    if max_depth == 1:
        return 1
    if len(root) == 1:  # ['a'] or ['B']
        key: str = root[0]
        if key in cfg.alphabet:
            return 1

        expanded: cfg_rhs = cfg.rules[key]

        sentential_forms = map(lambda rule: (rule,) if type(rule) is str else rule, expanded)
        return sum(map(lambda sentential_form: get_no_trees(tuple(sentential_form), max_depth - 1, cfg=cfg), sentential_forms))
    # root possible options : ['A'] ['A', 'B'] ['a'] ['a', 'S']
    return prod(map(lambda sub_tree: get_no_trees((sub_tree,), max_depth, cfg=cfg), root))


def map_to_space(index: int, x_bound, y_bound):  # wrap the original algorithm to make both bounds exclusive
    return cantors_extended_pi(index, x_bound - 1, y_bound)


def cantors_extended_pi(index: int, x_bound, y_bound):
    z = index

    # number of indices until x space is filled i.e (x, 0) is not available
    zx = (x_bound + 1) * (x_bound + 2) // 2

    # number of indices until y space is filled i.e (0, y) is not available
    zy = y_bound * (y_bound + 1) // 2

    # NOT 100% SURE: when to begin closing the bottom right corner
    zb = get_zb(y_bound, x_bound, zx, zy)

    if z >= zb:
        t, w = b_skip(z, x_bound, y_bound)
    elif zx <= z < zb:
        t, w = x_skip(z, x_bound)
    elif zy <= z < zb:
        t, w = y_skip(z, y_bound)
    else:
        t, w = simple(z)
    y = z - t
    x = w - y
    return x, y


def get_zb(yb, xb, zx, zy):
    if xb > yb - 1:
        return yb * (xb - yb + 1) + zy
    elif yb - 1 > xb:
        return (xb + 1) * (yb - xb - 1) + zx
    else:
        return zy


def b_skip(z, xb, yb):
    sb = xb ** 2 + yb ** 2
    wb = xb + yb
    r = 2 * wb + 1

    in_w_sqrt = r ** 2 - 8 * z - 4 * sb + 4 * yb - 4 * xb
    w = (r - ceil(sqrt(in_w_sqrt))) // 2

    t = ((2 * wb - 1) * w - w ** 2 - sb + wb) // 2
    return t, w


def x_skip(z, xb):  # Checked
    w = (2 * z + xb ** 2 + xb) // (2 * (xb + 1))
    t = (2 * w * xb - xb ** 2 + xb) // 2
    return t, w


def y_skip(z, yb):  # Checked
    w = (2 * z + yb ** 2 - yb) // (2 * yb)
    t = (2 * w * yb - yb ** 2 + yb) // 2
    return t, w


def simple(z):
    w = (floor(sqrt(8 * z + 1)) - 1) // 2
    t = w * (w + 1) // 2
    return t, w


def main():
    # import numpy as np
    # dim = (4, 2)
    # locs = np.ones(dim) * -1
    # missed = set()
    # for i in range(dim[0] * dim[1]):
    #     coords = map_to_space(i, *dim)
    #     try:
    #         locs[coords] = i
    #     except IndexError:
    #         missed.add((coords, i))
    # print(locs)
    # print(missed)
    # return
    agc_cfg = CFG(
        rules={
            'S': [['A', ], ['B', 'A']],
            'A': ['a', ['a', 'S']],
            'B': ['b']
        },
        start='S',
        alphabet={'a', 'b'}
    )
    results = dict()

    start, cfg = read_gram_file(r'..\benchmarks\AntlrJavaGrammar-1-1.gram')
    cnf = convert_to_cnf(start, cfg)

    cfg = cnf_10palindrome  # convert_cnf_to_limited_word_size(cnf_10palindrome, 3)
    sort_cfg_tree_wise(cfg, 10)
    for i in range(14):
        result = enum((cfg.start,), i, depth=30, cfg=cfg)
        if result is not None:
            key = ''.join(result)
        else:
            key = result
        if key not in results:
            results[key] = 0
        results[key] += 1

    print('dn')

    print(f'Sample \n{results}')
    rules = convert_cnf_to_list(cfg)

    for depth in range(max(map(lambda x: len(x) if x is not None else 0, results.keys())) + 1):
        print(f'checking length {depth}')
        for word in words_of_length(depth, cfg.alphabet):
            if ''.join(word) not in results and parse(word, rules):
                print(f'missed: {"".join(word)}')


if __name__ == '__main__':
    main()
