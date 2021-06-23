from match_checker import words_of_depth


def parse(chars, rules, start='S'):
    """
    CYK parser based on: https://en.wikipedia.org/wiki/CYK_algorithm#Algorithm
    """
    n = len(chars)
    table = [[[] for _ in range(n)] for _ in range(n)]

    # Identify terminal rules
    for char_index, char in enumerate(chars):
        for symbol_key, rule in rules.items():
            for rhs in rule:
                if rhs == char:
                    table[0][char_index].append(symbol_key)
                    break

    # fill the rest of the table
    for span in range(1, n):  # starting at the row after the terminals
        for span_start in range(n - span):  # In other words column
            for partition in range(span):  # Iterator for selecting combinations of squares for the left and right sides
                # check all the rules Ra -> Rb Rc
                for key, rule in rules.items():
                    for rhs in rule:
                        if type(rhs) is tuple:
                            left_side = rhs[0] in table[partition][span_start]
                            right_side = rhs[1] in table[span - partition - 1][span_start + partition + 1]
                            if left_side and right_side:
                                table[span][span_start].append(key)
    return start in table[-1][0]


def is_matching_cfg(a, b, alphabet, max_depth: int):
    for depth in range(max_depth):
        for word in words_of_depth(depth, alphabet):
            if parse(word, a) != parse(word, b):
                return False
    return True


cnf = {
    # start
    'S': [('X', 'A'), ('Y', 'B'), '1', '0'],
    # base
    'D': [('X', 'A'), ('Y', 'B'), '1', '0'],
    # alterone
    'A': [('D', 'X')],
    # alterzero
    'B': [('D', 'Y')],
    # one
    'X': ['1'],
    # zero
    'Y': ['0']
}

if __name__ == '__main__':
    from lark_testing import is_accepted, cnf as lark_cnf

    for length in range(20):

        for word in words_of_depth(length, ['1', '0']):
            joined_word = ''.join(word)
            is_parsed_by_me = parse(word, cnf)
            is_parsed_by_lark = is_accepted(lark_cnf, joined_word)
            if is_parsed_by_me != is_parsed_by_lark:
                print(f'me: {is_parsed_by_me}\tlark: {is_parsed_by_lark}\t word: {joined_word}')
        print('Done', length)
