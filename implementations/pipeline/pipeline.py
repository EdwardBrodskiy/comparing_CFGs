import numpy as np

from typing import Callable, Dict, Optional
from cfg import convert_cnf_to_list, CFG


class Pipeline:
    def __init__(self, a: CFG, b: CFG, max_depth: int):
        self._a = a
        self._b = b
        self.max_depth = max_depth

        self._list_rules = None

        self.data: Dict[str, np.ndarray] = {}

    @property
    def list_rules(self):
        if self._list_rules is not None:
            return self._list_rules
        self._list_rules = convert_cnf_to_list(self._a), convert_cnf_to_list(self._b)
        return self._list_rules


'''
INPUT: 2 CFGs that are to be compared a maximum depth and work of prior pipes
RETURN: Give back True or False if analysis was decisive otherwise return None 
'''
pipeline_function = Callable[[CFG, CFG, int, Pipeline], Optional[bool]]
