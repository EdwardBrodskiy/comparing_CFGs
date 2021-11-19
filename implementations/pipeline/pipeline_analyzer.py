from typing import Tuple, Optional
import logging
from cfg import CFG, cnf_10palindrome

from implementations.my_cyk_numpy import is_matching_cfg as numpy_is_matching_cfg
from implementations.pipeline.pipeline import Pipeline
from implementations.pipeline.pipeline_tools import PipelineDataManager

from implementations.pipeline.analyzers import rhs_lengths, subrule_match, subrule_match_optimized

from implementations.pipeline.comparators import alphabet_match, analysis_aggregator


def main():
    import cProfile
    import pstats
    from tools import convert_to_cnf, read_gram_file
    start, cfg = read_gram_file(r'..\..\benchmarks\AntlrJavaGrammar-1-1.gram')
    cnf = convert_to_cnf(start, cfg)
    with cProfile.Profile() as pr:
        is_matching_cfg(cnf, cnf, 7)
    stats = pstats.Stats(pr)
    stats.dump_stats(filename='pipeline.prof')


def is_matching_cfg(a: CFG, b: CFG, max_depth: int):
    pipeline = Pipeline(a, b, max_depth,
                        (
                            alphabet_match.method,  # TODO: are all the terminals reachable
                            rhs_lengths.method,
                            analysis_aggregator.method,
                            subrule_match_optimized.method,
                            analysis_aggregator.method,
                            # lambda *args: numpy_is_matching_cfg(*args[:-1])
                        ))
    return pipeline.evaluate()


def sanity_check_method(a: CFG, b: CFG, max_depth: int, pipeline: PipelineDataManager) -> Optional[bool]:
    print(
        f"{abs(pipeline.tables[rhs_lengths.method.key_word] - pipeline.tables[subrule_match_optimized.method.key_word][:-1, :-1]).mean()=}")

    return None


if __name__ == '__main__':
    logging.basicConfig(filename='main.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    main()
