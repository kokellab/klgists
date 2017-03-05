# coding=utf-8

import os
from typing import Iterator

def is_proper_file(path: str) -> bool:
    name = os.path.split(path)[1]
    return len(name) > 0 and name[0] not in {'.', '~', '_'}

def scantree(path: str, follow_symlinks: bool=False) -> Iterator[str]:
    """List the full path of every file not beginning with '.', '~', or '_' in a directory, recursively."""
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=follow_symlinks):
            yield from scantree(entry.path)
        elif is_proper_file(entry.path):
            yield entry.path
