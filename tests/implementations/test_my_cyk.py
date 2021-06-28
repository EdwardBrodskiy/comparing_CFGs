import unittest
from copy import deepcopy
import implementations.my_cyk as my_cyk

from tools import words_of_depth
from implementations.lark_testing import is_accepted, cnf as lark_cnf


class TestMyCyk(unittest.TestCase):
    def test_parser_on_10palindromes_to_depth_10(self):
        for length in range(10):
            for word in words_of_depth(length, ['1', '0']):
                joined_word = ''.join(word)
                is_parsed_by_me = my_cyk.parse(word, my_cyk.cnf)
                is_parsed_by_lark = is_accepted(lark_cnf, joined_word)
                self.assertEqual(is_parsed_by_me, is_parsed_by_lark)

    def test_is_matching_cfg_for_false_positives(self):
        self.assertTrue(my_cyk.is_matching_cfg(my_cyk.cnf, my_cyk.cnf, my_cyk.alph, 10))

    def test_is_matching_cfg_detect_difference(self):
        for key, rhs in my_cyk.cnf.items():
            for i in range(len(rhs)):
                bad_cnf = deepcopy(my_cyk.cnf)
                bad_cnf[key].pop(i)
                self.assertNotEqual(my_cyk.cnf, bad_cnf)
                self.assertFalse(my_cyk.is_matching_cfg(my_cyk.cnf, bad_cnf, my_cyk.alph, 7))


if __name__ == '__main__':
    unittest.main()
