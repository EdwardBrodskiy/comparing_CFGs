from typing import Iterator, List


def words_of_length(length, alphabet) -> Iterator[List[str]]:
    for letter in alphabet:
        if length < 1:
            break
        elif length == 1:
            yield letter
        else:
            for sub_word in words_of_length(length - 1, alphabet):
                yield [letter, *sub_word]
