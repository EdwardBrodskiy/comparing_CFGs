import unittest
import implementations.my_cfg_analyzer as my_cyk

from tests.implementations.tools_for_testing import inject_type_1_errors


class TestMyCyk(unittest.TestCase):

    def test_is_matching_cfg_for_false_positives(self):
        self.assertTrue(my_cyk.is_matching_cfg(my_cyk.cnf_10palindrome, my_cyk.cnf_10palindrome, my_cyk.alphabet10, 10))

    def test_is_matching_cfg_detect_difference(self):
        for bad_cnf in inject_type_1_errors(my_cyk.cnf_10palindrome):
            self.assertFalse(my_cyk.is_matching_cfg(my_cyk.cnf_10palindrome, bad_cnf, my_cyk.alphabet10, 7))


if __name__ == '__main__':
    unittest.main()
