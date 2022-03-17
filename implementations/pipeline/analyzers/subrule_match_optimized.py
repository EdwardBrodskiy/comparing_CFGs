from typing import List, Tuple, Dict, Set, Union
import numpy as np
import logging

from cfg import cfg_rhs, CFG

from implementations.pipeline.pipeline_tools import PipelineDataManager, PipelineMethodData


class UnknownValueError(Exception):
    pass


def match_subrules(a: CFG, b: CFG, max_depth: int, pipeline: PipelineDataManager) -> Tuple[bool, float]:
    list_rules_a, list_rules_b = pipeline.list_rules
    pipeline.tables[method.key_word] = generate_similarity_table_by_value_approach(list_rules_a, list_rules_b)
    return True, 0


def complexity_of_match_subrules(a: CFG, b: CFG, max_depth: int) -> int:
    return len(a.rules) * len(b.rules) * 3 * 12  # TODO: define in a more correct way


method = PipelineMethodData(
    match_subrules,
    complexity_of_match_subrules,
    'sub-rules-opt'
)


def generate_similarity_table_by_value_approach(a, b):
    """
    Approach solution by continuously re calculating the similarity table starting with everything at 0
    """
    table = np.zeros([len(a) + 1, len(b) + 1], dtype=np.float16)
    # TODO: Maybe check for how much the change happened?

    # find reverse referencing
    reverse_reference_a = get_reverse_reference(a)
    reverse_reference_b = get_reverse_reference(b)

    # derive iteration order sets
    iteration_order_a = generate_iteration_order(reverse_reference_a)
    iteration_order_b = generate_iteration_order(reverse_reference_b)

    logging.debug(f'{len(iteration_order_a)=}, {len(iteration_order_b)=}')

    # iterate over grammar making comparisons
    change = len(a) * len(b)
    counter = 0
    logging.debug(f'{0.01 * len(a) * len(b)=}')
    while change > 0.01 * len(a) * len(b):
        counter += 1
        change = 0
        for iteration_a in iteration_order_a:
            for iteration_b in iteration_order_b:
                for rule_a_index in iteration_a:
                    for rule_b_index in iteration_b:
                        if not (table[-1, rule_b_index] > .9 or table[rule_a_index, -1] > .9):
                            rhs_a = a[rule_a_index]
                            rhs_b = b[rule_b_index]

                            new_score = get_match_score(table, rhs_a, rhs_b, False)
                            change += abs(new_score - table[rule_a_index, rule_b_index])

                            table[rule_a_index, rule_b_index] = new_score
                            table[rule_a_index, -1] = table[rule_a_index, rule_b_index]
                            table[-1, rule_b_index] = table[rule_a_index, rule_b_index]
        logging.debug(f'At iteration {counter} the change is {change}')

    logging.debug(f'number of iterations {counter}')

    table[0, 0] = get_match_score(table, a[0], b[0], True)

    np.savetxt("subrule_match_optimized.csv", table, delimiter=",")
    return table[:-1, :-1]


def get_reverse_reference(rule_list):
    reverse_reference: Dict[Union[str, int], Set[int]] = {}
    for rule_a_key, rule_a_rhs in enumerate(rule_list):
        for rule in rule_a_rhs:
            referenced = set()
            if type(rule) is str:
                referenced.add(rule)
            else:
                referenced.add(rule[0])
                referenced.add(rule[1])
            for key in referenced:
                if key not in reverse_reference:
                    reverse_reference[key] = {rule_a_key}
                else:
                    reverse_reference[key].add(rule_a_key)
    return reverse_reference


def generate_iteration_order(reverse_reference):
    keys_referencing_terminals = [ref for k, ref in reverse_reference.items() if type(k) is str]
    iteration_order: List[Set[int]] = [set().union(*keys_referencing_terminals)]
    used_keys = iteration_order[0].copy()
    created_new_iteration = True
    while created_new_iteration:
        created_new_iteration = False
        keys_referencing_last_iteration = [reverse_reference[k] for k in iteration_order[-1] if k in reverse_reference]
        if keys_referencing_last_iteration:
            new_iteration = set.union(*keys_referencing_last_iteration) - used_keys
            if new_iteration:
                created_new_iteration = True
                used_keys |= new_iteration
                iteration_order.append(new_iteration)
    return iteration_order


# Obtain similarity value between two right hand sides
def get_match_score(table, rhs_a: cfg_rhs, rhs_b: cfg_rhs, cheat: bool) -> float:
    if len(rhs_a) > len(rhs_b):
        return get_match_score_ls(table, rhs_a, rhs_b, cheat)
    # TODO: there is a way to not use transpose see if that is significantly faster
    return get_match_score_ls(table.transpose(), rhs_b, rhs_a, cheat)


def get_match_score_ls(table, larger_rhs, smaller_rhs, cheat):
    matches: List[float] = [0 for _ in larger_rhs]

    for index, rhs_rule_a in enumerate(larger_rhs):
        for rhs_rule_b in smaller_rhs:
            match = get_rhs_rule_match_score(table, rhs_rule_a, rhs_rule_b, cheat)
            matches[index] = max(match, matches[index])

    return sum(matches) / len(matches)


def get_rhs_rule_match_score(table, rule_a, rule_b, cheat) -> float:
    if type(rule_a) == type(rule_b):
        if type(rule_a) is tuple:
            left = table[rule_a[0], rule_b[0]]
            right = table[rule_a[1], rule_b[1]]
            if not cheat and (left < 0 or right < 0):
                raise UnknownValueError
            left, right = abs(left), abs(right)  # TODO: this assumes it is -1 if not defined
            return left * right
        else:
            if rule_a == rule_b:
                return 1
    return 0


def main():
    from tools import convert_to_cnf, read_gram_file, convert_cnf_to_list
    from cfg import cnf_10palindrome
    test_grammar = CFG(
        rules={
            'S': [['A', 'B'], ['B', 'B']],
            'A': ['a', ['A', 'B']],
            'B': ['b']
        },
        alphabet={'a', 'b'},
        start='S'
    )

    a_cnf = convert_to_cnf(read_gram_file(r'..\..\..\benchmarks\AntlrJavaGrammar.gram'))
    a_cnf_list = convert_cnf_to_list(a_cnf)
    palindrome = convert_cnf_to_list(cnf_10palindrome)
    list_grammar = palindrome

    generate_similarity_table_by_value_approach(list_grammar, list_grammar)


if __name__ == '__main__':
    logging.basicConfig(filename='main.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    main()
