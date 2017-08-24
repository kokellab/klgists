# coding=utf-8

import pandas as pd
from typing import List, Union

def select_by_index(df: pd.DataFrame, key: Union[str, List[str]], value: Union[str, List[str]]) -> pd.DataFrame:
	return df[df.index.get_level_values(key) == value]

def group_by_index(df: pd.DataFrame, keys: Union[str, List[str]]) -> pd.core.groupby.DataFrameGroupBy:
	if isinstance(keys, str): keys = [keys]
	indices = {v: i for i, v in enumerate(df.index.names)}
	return df.groupby(level=[indices[key] for key in keys])

def set_column_sequence(dataframe: pd.DataFrame, col_seq: List[str]) -> pd.DataFrame:
	"""Moves some columns of a Pandas dataframe to the front, returning a copy.
	Returns: a copy of the dataframe with col_seq as the first columns
	"""
	return dataframe[col_seq + [c for c in dataframe.columns if c not in col_seq]]
