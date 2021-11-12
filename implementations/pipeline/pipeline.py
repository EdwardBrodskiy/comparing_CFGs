from typing import Dict, Tuple, List

from cfg import convert_cnf_to_list, CFG
from implementations.pipeline.pipeline_tools import PipelineMethodData, PipelineDataManager


class Pipeline:
    def __init__(self, a: CFG, b: CFG, max_depth: int, pipeline_methods: Tuple[PipelineMethodData, ...]):
        self._a = a
        self._b = b
        self._max_depth = max_depth

        self.data_manager = PipelineDataManager(self._a, self._b, self._get_next_method_in_pipeline)

        self.methods = pipeline_methods
        self.current_method_index = -1

    def _get_next_method_in_pipeline(self):
        if self.current_method_index + 1 < len(self.methods):
            return self.methods[self.current_method_index]
        return None

    def evaluate(self) -> bool:
        threshold = 1
        last_decision = True
        for i, pipe in enumerate(self.methods):
            self.current_method_index = i
            decision, certainty = pipe.method(self._a, self._b, self._max_depth, self.data_manager)
            print(f'pipe {pipe.method.__name__} returned {decision}\n')
            if certainty >= threshold:
                return decision
            last_decision = decision
        return last_decision
