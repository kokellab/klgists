# coding=utf-8

from typing import Iterable
import os

def scan_for_files(path: str, follow_symlinks: bool=False) -> Iterable[str]:
    """
    Using a generator, list all files in a directory or one of its subdirectories.
    Useful for iterating over files in a directory recursively if there are thousands of file.
    Warning: If there are looping symlinks, follow_symlinks will return an infinite generator.
    """
    for d in os.scandir(path):
        if d.is_dir(follow_symlinks=follow_symlinks):
            yield from scan_for_files(d.path)
        else:
            yield d.path
