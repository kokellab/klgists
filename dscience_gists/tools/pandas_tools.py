from typing import Union, Mapping, TypeVar, Any, Sequence, Dict, Optional
from pathlib import Path
import pandas as pd
from dscience_gists.support.extended_df import *
from dscience_gists.core import PathLike
from dscience_gists.core.exceptions import UserError
from dscience_gists.tools import VeryCommonTools
V = TypeVar('V')


class PandasTools(VeryCommonTools):

	@classmethod
	def cfirst(cls, df: pd.DataFrame, cols: Union[str, int, Sequence[str]]) -> pd.DataFrame:
		"""Moves some columns of a Pandas dataframe to the front, returning a copy.
		Returns: a copy of the dataframe with col_seq as the first columns
		"""
		if isinstance(cols, str) or isinstance(cols, int): cols = [cols]
		if len(df) == 0:  # will break otherwise
			return df
		else:
			return df[cols + [c for c in df.columns if c not in cols]]

	@classmethod
	def df_to_dict(cls, d: pd.DataFrame) -> Dict[Any, Any]:
		if len(d.columns) != 2:
			raise ValueError("Need exactly 2 columns (key, value); got {}".format(len(d.columns)))
		keys, values = d.columns[0], d.columns[1]
		return {
			getattr(r, keys): getattr(r, values)
			for r in d.itertuples()
		}

	@classmethod
	def csv_to_dict(cls, path: PathLike) -> Dict[Any, Any]:
		d = pd.read_csv(Path(path))
		return PandasTools.df_to_dict(d)

	@classmethod
	def dict_to_df(cls, dct: Mapping[Any, Any], keys: str = 'name', values: str = 'value') -> pd.DataFrame:
		dct = dict(dct)
		return pd.DataFrame.from_dict(dct, orient='index').reset_index().rename(columns={'index': keys, 0: values})

	@classmethod
	def dict_to_csv(cls, dct: Mapping[Any, Any], path: PathLike, keys: str = 'name', values: str = 'value') -> None:
		PandasTools.dict_to_df(dct, keys, values).to_csv(Path(path))

	@classmethod
	def extended_df(cls, df: pd.DataFrame, class_name: Optional[str] = None) -> ConvertibleExtendedDataFrame:
		"""
		Wrap `df` in an extended dataframe (ConvertibleExtendedDataFrame, which is its superclass).
		The returned Pandas DataFrame will have additional methods and better display in Jupyter.
		- If `df` is already a `ConvertibleExtendedDataFrame`, will just return it.
		- Otherwise:
			* Creates a new class with name `class_name` if `class_name` is non-null.
			* Otherwise wraps in a `FinalExtendedDataFrame`.
		:param df: Any Pandas DataFrame.
		:param class_name: Only applies if `df` isn't already a `ConvertibleExtendedDataFrame`
		:return: A copy of `df` of the new class
		"""
		if isinstance(df, ConvertibleExtendedDataFrame):
			return df
		elif isinstance(df, pd.DataFrame):
			if class_name is None:
				return FinalExtendedDataFrame(df)
			else:
				class X(TrivialExtendedDataFrame): pass
				X.__name__ = class_name
				return X(df)
		else:
			raise UserError("Invalid DataFrame type {}".format(df))

	@classmethod
	def series_to_df(cls, series, column: str) -> pd.DataFrame:
		return TrivialExtendedDataFrame(series).reset_index().rename(columns={0: column})


__all__ = ['PandasTools']
