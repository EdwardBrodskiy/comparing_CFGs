from cfg import CFG, cfg_rhs, cnf_10palindrome, convert_cnf_to_list
from tools import words_of_length, read_gram_file, convert_to_cnf
from typing import Union, Tuple
from math import prod, floor, sqrt
from implementations.my_cyk_numpy import parse

memo = {}


def memory(f):
    def helper(*args, **kwargs):
        key = (f.__name__, args)
        if key not in memo:
            memo[key] = f(*args, **kwargs)
        return memo[key]

    return helper


@memory
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
    # ['A', 'B']
    sub_enums = []  # TODO: this is not how it is done in the paper
    for sub_rule in root:
        t = get_no_trees((sub_rule,), depth, cfg=cfg)
        sub_enums.append(enum((sub_rule,), index % t, cfg=cfg))
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


def map_to_space(index: int, sub_trees: Tuple[int]):
    dunno = 0
    z = index
    zb = dunno
    zx = dunno
    zy = dunno
    if z > zb:
        t, w = bskip(z)
    elif zx <= z < zb:
        t, w = xskip(z)
    elif zy <= z < zb:
        t, w = yskip(z)
    else:
        t, w = simple(z)
    y = z - t
    x = w - y
    return x, y


def bskip(z):
    return 1, 1


def xskip(z):
    return 1, 1


def yskip(z):
    return 1, 1


def simple(z):
    return 1, 1


def main():
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

    cfg = cnf
    sort_cfg_tree_wise(cfg, 10)
    for i in range(50):
        key = ''.join(enum((cfg.start,), i, depth=30, cfg=cfg))
        if key not in results:
            results[key] = 0
        results[key] += 1
    rules = convert_cnf_to_list(cfg)
    print('dn')
    for depth in range(5):
        for word in words_of_length(depth, cfg.alphabet):
            if ''.join(word) not in results and parse(word, rules):
                print(f'missed: {word}')


if __name__ == '__main__':
    main()
