from typing import Union, List
import pandas as pd
from pandas.core.groupby import DataFrameGroupBy


def show_df_head(df: pd.DataFrame, n_rows:int=1) -> None:
	"""
	Pretty-print the head of a Pandas table in a Jupyter notebook and show its dimensions.
	Requires that IPython is installed.
	"""
	from IPython.display import display, Markdown
	display(Markdown("**whole table (below):** {} rows × {} columns".format(len(df), len(df.columns))))
	display(df.head(n_rows))


def select_by_index(df: pd.DataFrame, key: Union[str, List[str]], value: Union[str, List[str]]) -> pd.DataFrame:
	return df[df.index.get_level_values(key) == value]

def _set_column_sequence(dataframe: pd.DataFrame, col_seq: List[str]) -> pd.DataFrame:
	"""Moves some columns of a Pandas dataframe to the front, returning a copy.
	Returns: a copy of the dataframe with col_seq as the first columns
	"""
	if len(dataframe) == 0:  # will break otherwise
		return dataframe
	else:
		return dataframe[col_seq + [c for c in dataframe.columns if c not in col_seq]]

def cfirst(df: pd.DataFrame, cols: Union[str, int, List[str]]) -> pd.DataFrame:
	"""Moves some columns of a Pandas dataframe to the front, returning a copy.
	Returns: a copy of the dataframe with col_seq as the first columns
	"""
	if isinstance(cols, str) or isinstance(cols, int): cols = [cols]
	return _set_column_sequence(df, cols)


__all__ = ['show_df_head', 'select_by_index', 'cfirst']
