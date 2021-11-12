from typing import Tuple

from cfg import CFG
from implementations.pipeline.pipeline_tools import PipelineDataManager, PipelineMethodData


def is_matching_alphabet(a: CFG, b: CFG, max_depth: int, pipeline: PipelineDataManager) -> Tuple[bool, float]:
    if a.alphabet != b.alphabet:
        return False, 1
    return True, 0.1


method = PipelineMethodData(
    is_matching_alphabet,
    lambda *args: 1,
    None
)
