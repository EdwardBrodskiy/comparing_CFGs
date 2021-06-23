def parse(chars, symbols):
    n = len(chars)
    table = [[[False for _ in range(len(symbols))] for _ in range(n)] for _ in range(n)]

    for char_index, char in enumerate(chars):
        for symbol_index, symbol in enumerate(symbols):
            if symbol == char:
                table[0][char_index][symbol_index] = True
                break

    for span in range(1, n):
        for span_start in range(n - span):
            for partition in range(span):
                for rule_index, rule in enumerate(symbols):
                    if type(rule) is tuple:
                        if table[partition][span_start][rule[0]] and table[span - partition - 1][span + partition][rule[1]]:
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
    cfg = [

    ]
    print(parse(['0', '0'], [(1, 2), '0', '1']))
