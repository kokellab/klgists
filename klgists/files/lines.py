# coding=utf-8

import gzip, io
from typing import Iterator

def lines(file_name: str, known_encoding='utf-8') -> Iterator[str]:
    """Lazily read a text file or gzipped text file, decode, and strip any newline character (\n or \r).
    If the file name ends with '.gz' or '.gzip', assumes the file is Gzipped.
    Arguments:
        known_encoding: Applied only when decoding gzip
    """
    if file_name.endswith('.gz') or file_name.endswith('.gzip'):
        with io.TextIOWrapper(gzip.open(file_name, 'r'), encoding=known_encoding) as f:
            for line in f: yield line.rstrip('\n\r')
    else:
        with open(file_name, 'r') as f:
            for line in f: yield line.rstrip('\n\r')
