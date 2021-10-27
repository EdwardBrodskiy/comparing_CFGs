import unittest
import implementations.my_cyk as my_cyk
from tests.implementations.general_tester import GeneralTester, RequiredItems



if __name__ == '__main__':
    GeneralTester.items = RequiredItems(
        is_matching_cfg=my_cyk.is_matching_cfg,
        basic_cnf=my_cyk.cnf_10palindrome
    )
    unittest.main()
