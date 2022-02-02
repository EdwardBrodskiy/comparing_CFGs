from cfg import CFG, cfg_rhs, cnf_10palindrome
from typing import Union, Tuple
from math import prod

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

    sub_enums = list(map(lambda sub_rule: enum((sub_rule,), index, cfg=cfg), root))
    if not all(sub_enums):
        return None
    return tuple(item for sublist in sub_enums for item in sublist)


def choose(key: str, index: int, depth: int, cfg: CFG = None) -> Tuple[Tuple[str, ...], int]:
    expanded: cfg_rhs = cfg.rules[key]

    sentential_forms = list(map(lambda rule: (rule,) if type(rule) is str else rule, expanded))
    n = len(sentential_forms)

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
    if len(root) == 1:
        key: str = root[0]
        if key in cfg.alphabet:
            return 1

        expanded: cfg_rhs = cfg.rules[key]

        sentential_forms = map(lambda rule: (rule,) if type(rule) is str else rule, expanded)
        return sum(map(lambda sentential_form: get_no_trees(tuple(sentential_form), max_depth - 1, cfg=cfg), sentential_forms))

    return prod(map(lambda sub_tree: get_no_trees(sub_tree, max_depth, cfg=cfg), root))


def main():
    cfg = CFG(
        rules={
            'S': [['A', ], ['A', 'B']],
            'A': ['a', ['a', 'S']],
            'B': ['b']
        },
        start='S',
        alphabet={'a', 'b'}
    )
    results = dict()
    sort_cfg_tree_wise(cfg, 100)
    print(cfg)
    for i in range(10):
        key = str(enum((cfg.start,), i, cfg=cfg))
        if key not in results:
            results[key] = 0
        results[key] += 1
    print(results, len(results))
    print(get_no_trees(('S',), 166, cfg=cfg))


if __name__ == '__main__':
    main()
