# coding=utf-8

from .scan_for_files import scan_for_files  # see https://gist.github.com/dmyersturnbull/80845ba9ebab2da83963
from typing import Callable, Iterator

def find_only_file_matching(directory: str, matcher: Callable[[str], bool], file_iterator: Callable[[str], Iterator[str]]=scan_for_files) -> str:
    """Returns the full path of the matching file and raises an exception if none are found or more than 1 is found."""
    file = None
    for f in file_iterator(directory):
        if matcher(f):
            if file is not None:
                raise ValueError("Multiple matching files found in {}".format(directory))
            file = f
    if file is None:
        raise ValueError("No matching file found in {}".format(directory))
    return file
