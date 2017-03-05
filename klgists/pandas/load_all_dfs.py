# coding=utf-8

import pandas as pd
from .scan_for_files import scan_for_files  # see https://gist.github.com/dmyersturnbull/80845ba9ebab2da83963
from .head import head  # see https://gist.github.com/dmyersturnbull/035876942070ced4c565e4e96161be3e
from typing import Iterable, Optional, Callable, Dict, List


def load_all_dfs_as_dict(directory: str, suffixes: Iterable[str],
                 read_fn: Callable[[str], pd.DataFrame]=pd.read_csv) -> Dict[str, pd.DataFrame]:
    """Returns a dictionary mapping each filename suffix to a dataframe in a file matching that suffix.
    **Warning:** Each suffix must match a single filename (dataframe), or chaos will ensue."""
    dct = {}
    for f in scan_for_files(directory):
        for ko in suffixes:
            if f.endswith(ko):
                dct[ko] = read_fn(f)
    return dct
    
    
def load_all_dfs_as_list(directory: str, suffixes: List[str],
                 read_fn: Callable[[str], pd.DataFrame]=pd.read_csv, preview: bool=False) -> List[pd.DataFrame]:
    """Returns the DataFrames in order. An AssertionError will be thrown if a file is not found or two files matche a single suffix."""
    lst = [None for _ in suffixes]
    for f in scan_for_files(directory):
        for i, ko in enumerate(suffixes):
            if f.endswith(ko):
                if lst[i] is not None:
                    raise AssertionError("DataFrame for suffix {} found twice".format(ko))
                lst[i] = read_fn(f)
    n_found = len(list(filter(lambda d: d is not None, lst)))
    if n_found != len(suffixes):
        raise AssertionError("Required {} DataFrames; got {}".format(len(suffixes), n_found))
    if preview:
        for df in lst:
            head(df)
    return lst
