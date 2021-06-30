import unittest
import implementations.my_cyk_memo as my_cyk

from tests.implementations.tools_for_testing import word_and_result_from_nltk_10palindrome, inject_type_1_errors


class TestMyCyk(unittest.TestCase):

    def test_is_matching_cfg_for_false_positives(self):
        self.assertTrue(my_cyk.is_matching_cfg(my_cyk.cnf_10palindrome, my_cyk.cnf_10palindrome, my_cyk.alph, 10))

    def test_is_matching_cfg_detect_difference(self):
        for bad_cnf in inject_type_1_errors(my_cyk.cnf_10palindrome):
            self.assertFalse(my_cyk.is_matching_cfg(my_cyk.cnf_10palindrome, bad_cnf, my_cyk.alph, 7))


if __name__ == '__main__':
    unittest.main()
