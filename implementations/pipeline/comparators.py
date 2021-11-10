from typing import Optional

from cfg import CFG
from implementations.pipeline.pipeline import Pipeline


def is_matching_alphabet(a: CFG, b: CFG, max_depth: int, pipeline: Pipeline) -> Optional[bool]:
    if a.alphabet != b.alphabet:
        return False
    return None
