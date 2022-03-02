import unittest
import implementations.agc.main as agc

from tests.implementations.slow.slow_tester import SlowTester, RequiredItems

if __name__ == '__main__':
    SlowTester.items = RequiredItems(
        is_matching_cfg=agc.is_matching_cfg
    )
    unittest.main()
