from typing import List


def parse(chars, symbols):
    n = len(chars)
    table = [[[False for _ in range(len(symbols))] for _ in range(n)] for _ in range(n)]

    for char_index, char in enumerate(chars):
        for symbol_index, symbol in enumerate(symbols):
            for rhs in symbol:
                if rhs == char:
                    table[0][char_index][symbol_index] = True
                    break

    for span in range(1, n):
        for span_start in range(n - span):
            for partition in range(span):
                for rule_index, rule in enumerate(symbols):

                    for rhs in rule:
                        if type(rhs) is tuple:
                            left_side = table[partition][span_start][rhs[0]]
                            right_side = table[span - partition - 1][span + partition][rhs[1]]
                            if left_side and right_side:
                                table[span][span_start][rule_index] = True
    return table[-1][0][0]


if __name__ == '__main__':
    chomsky_grammar = '''
    start: one alterone | zero alterzero | one | zero 
    base: one alterone | zero alterzero | one | zero 
    alterone: base one
    alterzero: base zero
    one: "1"
    zero: "0"
    '''
    cnf = [
        # start
        [(4, 2), (5, 3), '1', '0'],
        # base
        [(4, 2), (5, 3), '1', '0'],
        # alterone
        [(1, 4)],
        # alterzero
        [(1, 5)],
        # one
        ['1'],
        # zero
        ['0']
    ]
    print(parse(['1', '0', '1'], cnf))
