import unittest
import implementations.my_cyk_memo_numpy as my_cyk

from tests.implementations.fast.general_tester import GeneralTester, RequiredItems

if __name__ == '__main__':
    GeneralTester.items = RequiredItems(
        is_matching_cfg=my_cyk.is_matching_cfg,
        basic_cnf=my_cyk.cnf_10palindrome
    )
    unittest.main()
