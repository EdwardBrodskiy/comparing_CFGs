import numpy as np
from math import inf
from dataclasses import dataclass
from typing import Callable, Optional, Dict, Tuple, Any, Union

from cfg import convert_cnf_to_list, CFG


class PipelineDataManager:
    def __init__(self, a: CFG, b: CFG, max_depth: int, get_next_method):
        self._a = a
        self._b = b
        self._max_depth = max_depth

        self._list_rules = None
        self._get_next_method = get_next_method

        self.tables: Dict[str, np.ndarray] = {}
        self.data: Dict[str, Any] = {}

    def get_next_method_complexity(self) -> Union[float, int]:
        next_method = self._get_next_method()
        if next_method is not None:
            return next_method.complexity(self._a, self._b, self._max_depth)
        return inf

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
pipeline_function = Callable[[CFG, CFG, int, PipelineDataManager], Tuple[bool, float]]

complexity_function = Callable[[CFG, CFG, int], int]


@dataclass
class PipelineMethodData:
    method: pipeline_function  # the method for the pipeline to call
    complexity: complexity_function  # a method to approximate how long a function will take to run
    key_word: Optional[str]  # key used to store information on the pipeline
