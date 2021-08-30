import unittest
import os

import tools


class TestTools(unittest.TestCase):
    def test_number_of_words_in_words_of_length(self):
        for length in range(1, 7):
            for no_letters in range(1, 12):
                alphabet = [chr(i + 65) for i in range(no_letters)]
                generated_words = list(tools.words_of_length(length, alphabet))
                no_words = len(generated_words)
                self.assertEqual(no_letters ** length, no_words, msg=f'{no_words} should be {no_letters}^{length}={no_letters ** length}')

    def test_uniqueness_of_words_in_words_of_length(self):
        for length in range(0, 7):
            for no_letters in range(0, 12):
                alphabet = [chr(i + 65) for i in range(no_letters)]
                generated_words = list(tools.words_of_length(length, alphabet))
                set_of_generated_words = set(map(lambda x: ''.join(x), generated_words))
                self.assertEqual(len(generated_words), len(set_of_generated_words))

    def test_cnf_correctness_for_all_cfgs(self):
        os.chdir(os.path.join('..', 'benchmarks'))
        gram_files = list(filter(lambda f: '.gram' == f[-5:], os.listdir()))
        for file_name in gram_files:
            self.assertTrue(tools.is_cnf(*tools.convert_to_cnf(*tools.read_gram_file(file_name))), msg=f'failed for file {file_name}')
