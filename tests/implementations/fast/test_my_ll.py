import unittest
import implementations.my_ll as my_ll
from tests.implementations.fast.general_tester import GeneralTester, RequiredItems

if __name__ == '__main__':
    GeneralTester.items = RequiredItems(
        is_matching_cfg=my_ll.is_matching_cfg,
        basic_cnf=my_ll.ll_cfg
    )
    unittest.main()
