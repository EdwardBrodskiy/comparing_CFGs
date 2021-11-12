from typing import Optional

from cfg import CFG
from implementations.pipeline.pipeline_tools import PipelineDataManager, PipelineMethodData


def is_matching_alphabet(a: CFG, b: CFG, max_depth: int, pipeline: PipelineDataManager) -> Optional[bool]:
    if a.alphabet != b.alphabet:
        return False
    return None


method = PipelineMethodData(
    is_matching_alphabet,
    lambda *args: 1,
    None
)
