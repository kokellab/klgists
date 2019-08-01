from __future__ import annotations
import typing
from typing import Sequence, Set, Any, Callable, Union, Iterable
import multiprocessing
import pandas as pd
from natsort import ns, natsorted
from pandas.core.frame import DataFrame as _InternalDataFrame
from klgists.pandas import cfirst as _cfirst
from klgists.common import only as _only
from klgists.pandas.groupby_parallel import groupby_parallel as _groupby_parallel
import klgists.common.abcd as abcd


class InvalidExtendedDataFrameError(Exception): pass


class PrettyInternalDataFrame(_InternalDataFrame, abcd.ABC):
	"""
	A DataFrame with an overridden _repr_html_ that shows the dimensions at the top.
	"""

	def _repr_html_(self):
		"""
		Renders HTML for display() in Jupyter notebooks.
		Jupyter automatically uses this function.
		:return: Just a string, which will be wrapped in HTML
		"""
		return "<strong>{}: {}</strong>\n{}".format(self.__class__.__name__, self._dims(), super(PrettyInternalDataFrame, self)._repr_html_(), len(self))

	def _dims(self) -> str:
		"""
		:return: A text description of the dimensions of this DataFrame
		"""
		# we could handle multi-level columns, but they're quite rare, and the number of rows is probably obvious when looking at it
		if len(self.index.names) > 1:
			return "{} rows × {} columns, {} index columns".format(len(self), len(self.columns), len(self.index.names))
		else:
			return "{} rows × {} columns".format(len(self), len(self.columns))


class BaseExtendedDataFrame(PrettyInternalDataFrame, abcd.ABC):
	"""
	An abstract Pandas DataFrame subclass with additional methods.
	"""
	def __init__(self, data=None, index=None, columns=None, dtype=None, copy=False):
		super(BaseExtendedDataFrame, self).__init__(data=data, index=index, columns=columns, dtype=dtype, copy=copy)

	@classmethod
	def _change(cls, df):
		df.__class__ = cls
		return df

	def n_rows(self) -> int:
		return len(self)

	def n_columns(self) -> int:
		return len(self.columns)

	def n_index_columns(self) -> int:
		return len(self.index.names)

	def apply_parallel(
			self,
			function: Callable[[typing.Tuple[str, pd.DataFrame]], Union[pd.DataFrame, pd.Series]],
			n_cores: int = multiprocessing.cpu_count() - 1,
			logger: Callable[[str], None] = print,
			**groupby_kwargs
	) -> pd.DataFrame:
		"""
		Performs Pandas `groupby` followed by `apply(function)`, using Multiprocessing to split over `n_cores` CPUs.
		:param function:
		:param n_cores:
		:param logger:
		:param groupby_kwargs: Will be passed to Pandas groupby.
		:return:
		"""
		return _groupby_parallel(self.groupby(**groupby_kwargs), function, num_cpus=n_cores, logger=logger)

	def only(self, column: str) -> Any:
		"""
		Returns the single unique value in a column.
		Raises an error if zero or more than one value is in the column.
		:param column: The name of the column
		:return: The value
		"""
		return _only(self[column].unique())


class ConvertibleExtendedDataFrame(BaseExtendedDataFrame, abcd.ABC):
	"""
	An extended DataFrame with convert() and vanilla() methods.
	"""
	pass

	@classmethod
	@abcd.override_recommended
	def convert(cls, df: pd.DataFrame):
		"""
		Converts a vanilla Pandas DataFrame to cls.
		Sets the index appropriately, permitting the required columns and index names to be either columns or index names.
		Explicitly sets df.__class__ to cls; this is done IN PLACE. This will generally not affect the passed df functinally, but could.
		:param df: The Pandas DataFrame or member of cls; will have its __class_ change but will otherwise not be affected
		:return: A non-copy
		"""
		df.__class__ = cls
		return df

	def cfirst(self, cols: Sequence[str]):
		"""
		Returns a new DataFrame with the specified columns appearing first.
		:param cols: A list of columns
		:return: A non-copy
		"""
		# noinspection PyTypeChecker
		return self.convert(_cfirst(self, cols))

	def sort_natural(self, column: str, alg: int = ns.INT):
		df = self.copy().reset_index()
		zzz = natsorted([s for s in df[column]], alg=alg)
		df['__sort'] = df[column].map(lambda s: zzz.index(s))
		df.__class__ = self.__class__
		df = df.sort_values('__sort').drop_cols(['__sort', 'level_0', 'index'])
		return self.convert(df)

	def sort_natural_index(self, alg: int = ns.INT):
		df = self.copy().reset_index()
		zzz = natsorted([s for s in df.index], alg=alg)
		df['__sort'] = df.index.map(lambda s: zzz.index(s))
		df.__class__ = self.__class__
		df = df.sort_values('__sort').drop_cols(['__sort', 'level_0', 'index'])
		return self.convert(df)

	def drop_cols(self, cols: Iterable[str]):
		df = self.copy()
		if isinstance(cols, str): cols = [cols]
		for c in cols:
			if c in self.columns:
				df = df.drop(c, axis=1)
		return self.convert(df)

	@classmethod
	@abcd.override_recommended
	def vanilla(cls, df: BaseExtendedDataFrame) -> pd.DataFrame:
		"""
		Converts a vanilla Pandas DataFrame to cls.
		Returns a copy (see note below though).
		:param df: The BaseExtendedDataFrame or member of cls; will have its __class_ change but will otherwise not be affected
		:return: A true, shallow copy with its __class__ set to pd.DataFrame
		"""
		df = df.copy()
		df.__class__ = pd.DataFrame
		return df

	def to_vanilla(self, df: BaseExtendedDataFrame) -> pd.DataFrame:
		"""
		Instance alias of BaseExtendedDataFrame.vanilla.
		Returns a copy (see note below though).
		:param df: The BaseExtendedDataFrame or member of cls; will have its __class_ change but will otherwise not be affected
		:return: A true, shallow copy with its __class__ set to pd.DataFrame
		"""
		return self.__class__.vanilla(df)


class TrivialExtendedDataFrame(ConvertibleExtendedDataFrame):
	"""
	A concrete BaseExtendedDataFrame that does not require special columns.
	Overrides a number of DataFrame methods to convert before returning.
	"""

	def __getitem__(self, item):
		if isinstance(item, str) and item in self.index.names:
			return self.index.get_level_values(item)
		else:
			return super(TrivialExtendedDataFrame, self).__getitem__(item)

	def drop_duplicates(self, **kwargs):
		return self._change(super(ConvertibleExtendedDataFrame, self).drop_duplicates(**kwargs))

	def reindex(self, *args, **kwargs):
		return self._change(super(ConvertibleExtendedDataFrame, self).reindex(*args, **kwargs))

	def sort_values(self, by, axis=0, ascending=True, inplace=False,  kind='quicksort', na_position='last'):
		return self._change(super(ConvertibleExtendedDataFrame, self).sort_values(by=by, axis=axis, ascending=ascending, inplace=inplace, kind=kind, na_position=na_position))

	def reset_index(self, level=None, drop=False, inplace=False, col_level=0, col_fill=''):
		return self._change(super(ConvertibleExtendedDataFrame, self).reset_index(level=level, drop=drop, inplace=inplace, col_level=col_level, col_fill=col_fill))

	def set_index(self, keys, drop=True, append=False, inplace=False, verify_integrity=False):
		return self._change(super(ConvertibleExtendedDataFrame, self).set_index(keys=keys, drop=drop, append=append, inplace=inplace, verify_integrity=verify_integrity))

	def dropna(self, axis=0, how='any', thresh=None, subset=None, inplace=False):
		return self._change(super(ConvertibleExtendedDataFrame, self).dropna(axis=axis, how=how, thresh=thresh, subset=subset, inplace=inplace))

	def fillna(self, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None, **kwargs):
		return self._change(super(ConvertibleExtendedDataFrame, self).fillna(value=value, method=method, axis=axis, inplace=inplace, limit=limit, downcast=downcast, **kwargs))

	def ffill(self, axis=None, inplace=False, limit=None, downcast=None):
		return self._change(super(ConvertibleExtendedDataFrame, self).ffill(axis=axis, inplace=inplace, limit=limit, downcast=downcast))

	def bfill(self, axis=None, inplace=False, limit=None, downcast=None):
		return self._change(super(ConvertibleExtendedDataFrame, self).bfill(axis=axis, inplace=inplace, limit=limit, downcast=downcast))

	def abs(self):
		return self._change(super(ConvertibleExtendedDataFrame, self).abs())

	def rename(self, *args, **kwargs):
		return self._change(super(ConvertibleExtendedDataFrame, self).rename(*args, **kwargs))

	def replace(self, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
		return self._change(super(ConvertibleExtendedDataFrame, self).replace(to_replace=to_replace, value=value, inplace=inplace, limit=limit, regex=regex, method=method))

	def applymap(self, func):
		return self._change(super(ConvertibleExtendedDataFrame, self).applymap(func))

	def astype(self, dtype, copy=True, errors='raise', **kwargs):
		return self._change(super(ConvertibleExtendedDataFrame, self).astype(dtype=dtype, copy=copy, errors=errors, **kwargs))

	def drop(self, labels=None, axis=0, index=None, columns=None, level=None, inplace=False, errors='raise'):
		return self._change(super(ConvertibleExtendedDataFrame, self).drop(labels=labels, axis=axis, index=index, columns=columns, level=level, inplace=inplace, errors=errors))


@abcd.final
class FinalExtendedDataFrame(TrivialExtendedDataFrame):
	"""
	A ready-to-go TrivialExtendedDataFrame that should not be overridden.
	"""


class ExtendedDataFrame(ConvertibleExtendedDataFrame):
	"""
	A concrete BaseExtendedDataFrame that has required columns and index names.
	"""

	@classmethod
	def convert(cls, df: pd.DataFrame, require_full: bool = False):
		"""
		Converts a vanilla Pandas DataFrame to cls.
		Returns a copy (see note below though).
		Sets the index appropriately, permitting the required columns and index names to be either columns or index names.
		Explicitly sets df.__class__ to cls; this is done IN PLACE. This will generally not affect the passed df functinally, but could.
		:param df: The Pandas DataFrame or member of cls; will have its __class_ change but will otherwise not be affected
		:param require_full: Raise a InvalidExtendedDataFrameError if a required column or index name is missing
		:return: A copy
		"""
		if not isinstance(df, pd.DataFrame):
			raise TypeError("Can't convert {} to {}".format(type(df), cls.__name__))
		# first always reset the index so we can manage what's in the index vs columns
		def drop(d):
			for x in cls.columns_to_drop():
				if x in d.columns:
					d = d.drop(x, axis=1)
			return d
		df = drop(drop(df).reset_index())
		# check that it has every required column and index name
		if require_full:
			cls._check(df, set(list(cls.required_index_names()) + list(cls.required_columns())))
		# set index columns and used preferred order
		res = []
		# here we keep the order of reserved if it contains all of required
		for c in list(cls.reserved_index_names()) + list(cls.required_index_names()):
			if c not in res and c in df.index.names:
				res.append(c)
		if len(res) > 0:  # raises an error otherwise
			df = df.set_index(res)
		# now set the regular column order
		res = []  # re-use the same variable name
		for c in list(cls.reserved_columns()) + list(cls.required_columns()):
			if c not in res and c in df.columns:
				res.append(c)
		df = _cfirst(df, res)
		# now change the class
		df.__class__ = cls
		return df

	def sort_values(self, by, axis=0, ascending=True, inplace=False, kind='quicksort', na_position='last'):
		got = super(ExtendedDataFrame, self).sort_values(by=by, axis=axis, ascending=ascending, inplace=inplace, kind=kind, na_position=na_position)
		got.__class__ = self.__class__
		return got

	@classmethod
	def _check(cls, df, required: Set[str]):
		for c in required:
			if c not in df.columns:
				raise InvalidExtendedDataFrameError("Missing column or index name {}".format(c))

	@classmethod
	@abcd.override_recommended
	def required_columns(cls) -> Sequence[str]:
		return []

	@classmethod
	@abcd.override_recommended
	def reserved_columns(cls) -> Sequence[str]:
		return []

	@classmethod
	@abcd.override_recommended
	def reserved_index_names(cls) -> Sequence[str]:
		return []

	@classmethod
	@abcd.override_recommended
	def required_index_names(cls) -> Sequence[str]:
		return []

	@classmethod
	@abcd.override_recommended
	def columns_to_drop(cls) -> Sequence[str]:
		return []


__all__ = ['BaseExtendedDataFrame', 'TrivialExtendedDataFrame', 'FinalExtendedDataFrame', 'ExtendedDataFrame', 'InvalidExtendedDataFrameError', 'ns']
