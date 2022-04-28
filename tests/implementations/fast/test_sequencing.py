import unittest
import implementations.sequencing as seq

from tests.implementations.fast.general_tester import GeneralTester, RequiredItems

if __name__ == '__main__':
    GeneralTester.items = RequiredItems(
        is_matching_cfg=seq.is_matching_cfg,
        basic_cnf=seq.cnf_10palindrome
    )
    unittest.main()
