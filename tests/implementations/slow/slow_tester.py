import unittest
from dataclasses import dataclass
from cfg import type_is_matching_cfg, CFG
from tests.implementations.tools_for_testing import inject_type_1_errors, get_alphabet, inject_type_2_errors, inject_type_3_errors
from tools import read_gram_file, convert_to_cnf
import logging


@dataclass
class RequiredItems:
    is_matching_cfg: type_is_matching_cfg = None


class SlowTester(unittest.TestCase):
    items: RequiredItems = None

    def setUp(self) -> None:
        start, cfg = read_gram_file(r'..\..\..\benchmarks\AntlrJavaGrammar-1-1.gram')
        start2, cfg2 = read_gram_file(r'..\..\..\benchmarks\C11Grammar1.gram')
        self.cfg = CFG(cfg, get_alphabet(cfg), start)
        self.cfg2 = CFG(cfg2, get_alphabet(cfg2), start2)
        self.cnf2 = convert_to_cnf(self.cfg2.start, self.cfg2.rules)
        self.cnf = convert_to_cnf(self.cfg.start, self.cfg.rules)

    # def test_is_matching_cfg_for_false_positives(self):
    #     if self.items is None:
    #         raise NotImplementedError
    #     self.assertTrue(self.items.is_matching_cfg(self.cnf, self.cnf, 5))

    def test_is_matching_cfg_detect_difference_between_2_cfgs(self):
        if self.items is None:
            raise NotImplementedError
        self.assertFalse(self.items.is_matching_cfg(self.cnf, self.cnf2, 7))

    # def test_is_matching_cfg_detect_difference_of_type_1_errors(self):
    #     if self.items is None:
    #         raise NotImplementedError
    #     for bad_cnf in inject_type_1_errors(self.cnf, sample_size=1, be_consistent=False):
    #         self.assertFalse(self.items.is_matching_cfg(self.cnf, bad_cnf, 20))

    # def test_is_matching_cfg_detect_difference_of_type_2_errors(self):
    #     if self.items is None:
    #         raise NotImplementedError
    #     for bad_cfg in inject_type_2_errors(self.cfg, sample_size=1):
    #         bad_cnf = convert_to_cnf(bad_cfg.start, bad_cfg.rules)
    #         self.assertFalse(self.items.is_matching_cfg(self.cnf, bad_cnf, 12))

    # def test_is_matching_cfg_detect_difference_of_type_3_errors(self):
    #     if self.items is None:
    #         raise NotImplementedError
    #     for bad_cfg in inject_type_3_errors(self.cfg, sample_size=1):
    #         bad_cnf = convert_to_cnf(bad_cfg.start, bad_cfg.rules)
    #         logging.info(f'{len(self.cnf.rules)=} {len(bad_cnf.rules)=}')
    #         self.assertFalse(self.items.is_matching_cfg(self.cnf, bad_cnf, 12))


logging.basicConfig(filename='slow_main.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
