import unittest
import implementations.my_cyk_numpy as my_cyk

from tests.implementations.tools_for_testing import word_and_result_from_nltk_10palindrome, inject_type_1_errors


class TestMyCyk(unittest.TestCase):
    def test_parser_on_10palindromes_to_depth_10(self):
        for word, result in word_and_result_from_nltk_10palindrome(10):
            is_parsed_by_me = my_cyk.parse(word, my_cyk.cnf_10palindrome)
            self.assertEqual(is_parsed_by_me, result)

    def test_is_matching_cfg_for_false_positives(self):
        self.assertTrue(my_cyk.is_matching_cfg(my_cyk.cnf_10palindrome, my_cyk.cnf_10palindrome, my_cyk.alphabet10, 10))

    def test_is_matching_cfg_detect_difference(self):
        for bad_cnf in inject_type_1_errors(my_cyk.cnf_10palindrome):
            self.assertFalse(my_cyk.is_matching_cfg(my_cyk.cnf_10palindrome, bad_cnf, my_cyk.alphabet10, 7))


if __name__ == '__main__':
    unittest.main()
