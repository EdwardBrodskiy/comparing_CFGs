def words_of_depth(depth, alphabet):
    for letter in alphabet:
        if depth == 0:
            yield letter
        else:
            for sub_word in words_of_depth(depth - 1, alphabet):
                yield [letter, *sub_word]
