from cfg import CFG, cfg_rhs, convert_cnf_to_list
from tools import words_of_length, read_gram_file, convert_to_cnf, convert_cnf_to_limited_word_size
from typing import Union, Tuple
from math import prod
from implementations.my_cyk_numpy import parse
from implementations.agc.index_mapper import map_to_space
from copy import deepcopy


def memory(f):
    def helper(self, *args, **kwargs):
        key = (f.__name__, args)
        if key not in self.memo:
            self.memo[key] = f(self, *args, **kwargs)
        return self.memo[key]

    return helper


class Enum:
    def __init__(self, cfg: CFG, max_depth):
        self.memo = {}
        self.max_depth = max_depth + 1  # make it inclusive
        self.cfg = deepcopy(cfg)
        self.sort_cfg_tree_wise()
        self.max_index = self.get_no_trees((self.cfg.start,), self.max_depth)

    def generate(self, index: int):
        return self.enum((self.cfg.start,), index, self.max_depth)

    @memory
    def enum(self, root: Tuple[str, ...], index: int, depth) -> Union[Tuple[str, ...], None]:
        if len(root) == 1:
            key: str = root[0]
            # For a terminal a belonging to a grammar, Enum[a] is defined as {0 → leaf (a)}.
            if key in self.cfg.alphabet:
                if index == 0:
                    return tuple((key,))
                return None

            return self.enum(*self.choose(key, index, depth), depth - 1)

        if len(root) != 2:  # root is expected to be size to as all expansions of a CNF are size 2 or 1
            raise Exception('Ensure grammar is in CNF')

        # get the index space required for A and B in AB
        a_trees, b_trees = self.get_no_trees((root[0],), depth), self.get_no_trees((root[1],), depth)
        if a_trees * b_trees <= index:
            return None  # index is past all possible derivations

        cartesian_expansion_coords = map_to_space(index, a_trees, b_trees)

        # derive enum(A)[j0] and enum(B)[j1] from enum(AB)[i]
        sub_enums = tuple(map(lambda j, sub_rule: self.enum((sub_rule,), j, depth),
                              cartesian_expansion_coords, root))

        if not all(sub_enums):  # TODO: maybe redundant
            return None

        return tuple(item for sublist in sub_enums for item in sublist)

    def choose(self, key: str, index: int, depth: int) -> Tuple[Tuple[str, ...], int]:
        # '#t' is used to denote the number of parse trees belonging to the right-hand-sides calculated by function 'get_no_trees'

        # extract all sentential forms which are the rhs of the given key
        # NOTE: in ascending order of #t (sorted prior)
        sentential_forms = list(map(lambda rule: (rule,) if type(rule) is str else rule, self.cfg.rules[key]))
        n = len(sentential_forms)

        # let b0 = 0, and b1, · · · , bn = #t(α0), · · · , #t(αn−1)
        trees: Tuple[int, ...] = (
            0, *list(map(lambda sentential_form: self.get_no_trees(tuple(sentential_form), depth), sentential_forms)))

        # wrap helper to better fit original definition
        def i(bound):
            return self.helper_index(bound, n, trees)

        # Find the smallest rhs tree that would not return out of bounds (None)
        k = 0
        while k < n and i(k) <= index:
            k += 1
        k -= 1

        # get the sub index in the bound
        q = (index - i(k)) // (n - k)
        # get the offset for which rule to choose from the remaining
        r = (index - i(k)) % (n - k)

        return tuple(sentential_forms[k + r]), trees[k] + q

    @staticmethod
    def helper_index(m: int, n: int, b: Tuple[int]) -> int:
        return b[m] * (n - m + 1) + sum(b[: m])

    def sort_cfg_tree_wise(self):
        for key, rhs in self.cfg.rules.items():
            self.cfg.rules[key] = sorted(rhs,
                                         key=lambda rule: self.get_no_trees((rule,), self.max_depth) if type(
                                             rule) is str else self.get_no_trees(
                                             tuple(rule), self.max_depth))

    @memory
    def get_no_trees(self, root: Tuple[str, ...], depth: int) -> int:
        if len(root) == 1:  # ['a'] or ['B']
            key: str = root[0]
            if key in self.cfg.alphabet:
                return 1
            if depth <= 1:
                return 1
            expanded: cfg_rhs = self.cfg.rules[key]

            sentential_forms = map(lambda rule: (rule,) if type(rule) is str else rule, expanded)
            return sum(map(lambda sentential_form: self.get_no_trees(tuple(sentential_form), depth - 1), sentential_forms))
        if depth <= 1:
            return 0
        # root possible options : ['A'] ['A', 'B'] ['a'] ['a', 'S']
        return prod(map(lambda sub_tree: self.get_no_trees((sub_tree,), depth), root))


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

    cfg = read_gram_file(r'..\..\benchmarks\C11Grammar1.gram')
    cnf = convert_to_cnf(cfg)

    cfg = cnf  # convert_cnf_to_limited_word_size(cnf, 6)
    enum = Enum(cfg, 3)
    nones = ''
    print(f'{enum.max_index=}')
    for i in range(enum.max_index):
        result = enum.generate(i)

        key = ''.join(result) if result is not None else result

        results[key] = results[key] + i if key in results else 0

        nones += '' + str(len(result)) if result is not None else '_'

    print(f'done {len(results)=}')

    print(nones)

    # print(f'Sample \n{results}')
    rules = convert_cnf_to_list(cfg)

    max_length = max(map(lambda x: len(x) if x is not None else 0, results.keys()))
    print(f'{max_length=}')
    for depth in range(max_length + 1):
        print(f'checking length {depth}')
        for word in words_of_length(depth, cfg.alphabet):
            if ''.join(word) not in results and parse(word, rules):
                print(f'missed: {"".join(word)}')


if __name__ == '__main__':
    main()
