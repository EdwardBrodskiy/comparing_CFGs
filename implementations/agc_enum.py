from cfg import CFG, cfg_rhs, cnf_10palindrome
from typing import Union, Tuple

memo = {}


def memory(f):
    def helper(*args, **kwargs):
        if args not in memo:
            memo[args] = f(*args, **kwargs)
        return memo[args]

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

        expanded: cfg_rhs = cfg.rules[key]

        selected_path = expanded[index % len(expanded)]

        return enum(tuple(selected_path), index // len(expanded), cfg=cfg)

    sub_enums = list(map(lambda sub_rule: enum((sub_rule,), index, cfg=cfg), root))
    if not all(sub_enums):
        return None
    return tuple(item for sublist in sub_enums for item in sublist)


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
    for i in range(400):
        key = str(enum((cfg.start,), i, cfg=cfg))
        if key not in results:
            results[key] = 0
        results[key] += 1
    print(results, len(results))


if __name__ == '__main__':
    main()
