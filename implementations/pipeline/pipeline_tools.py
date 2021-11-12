import numpy as np
from dataclasses import dataclass
from typing import Callable, Optional, Dict, Tuple

from cfg import convert_cnf_to_list, CFG


class PipelineDataManager:
    def __init__(self, a: CFG, b: CFG, get_next_method):
        self._a = a
        self._b = b
        self._list_rules = None
        self._get_next_method = get_next_method

        self.data: Dict[str, np.ndarray] = {}

    def get_next_method(self):
        return self._get_next_method()

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
