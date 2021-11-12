import unittest
from dataclasses import dataclass
from cfg import type_is_matching_cfg, CFG
from tests.implementations.tools_for_testing import inject_type_1_errors
import logging


@dataclass
class RequiredItems:
    is_matching_cfg: type_is_matching_cfg = None
    basic_cnf: CFG = None


class GeneralTester(unittest.TestCase):
    items: RequiredItems = None

    def test_is_matching_cfg_for_false_positives(self):
        if self.items is None:
            raise NotImplementedError
        self.assertTrue(self.items.is_matching_cfg(self.items.basic_cnf, self.items.basic_cnf, 10))

    def test_is_matching_cfg_detect_difference(self):
        if self.items is None:
            raise NotImplementedError
        for bad_cnf in inject_type_1_errors(self.items.basic_cnf):
            self.assertFalse(self.items.is_matching_cfg(self.items.basic_cnf, bad_cnf, 7))


logging.basicConfig(filename='main.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
