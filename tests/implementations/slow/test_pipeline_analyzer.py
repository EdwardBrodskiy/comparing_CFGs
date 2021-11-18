import unittest
import implementations.pipeline.pipeline_analyzer as my_cyk

from tests.implementations.slow.slow_tester import SlowTester, RequiredItems

if __name__ == '__main__':
    SlowTester.items = RequiredItems(
        is_matching_cfg=my_cyk.is_matching_cfg
    )
    unittest.main()
