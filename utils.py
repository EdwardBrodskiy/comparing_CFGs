from tools import read_gram_file
from cfg import cfg_type
from typing import Iterator, Optional, Tuple
import os


def load_gram_files(amount: Optional[int] = None, path: str = os.path.join('.', 'benchmarks')) -> Iterator[
    Tuple[str, Tuple[str, cfg_type]]]:
    if amount is not None:
        gram_files = list(filter(lambda f: '.gram' == f[-5:], os.listdir(path)))[:amount]
    else:
        gram_files = list(filter(lambda f: '.gram' == f[-5:], os.listdir(path)))

    for gram_file in gram_files:
        cfg = read_gram_file(os.path.join(path, gram_file))
        yield gram_file[:-5], cfg


def main():
    for name, cfg in load_gram_files():
        print(f'{name=}\t|\t{str(cfg)[:80]} ...')


if __name__ == '__main__':
    main()
