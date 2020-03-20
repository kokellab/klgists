from __future__ import annotations
import logging
from typing import Set, Sequence, Union, Callable, Mapping
from copy import deepcopy
from pathlib import Path
import numpy as np
import pandas as pd
from clana.visualize_cm import simulated_annealing
from dscience.core import PathLike
from dscience.core.exceptions import *
from dscience.core.extended_df import *
from dscience.core.chars import *

logger = logging.getLogger('dscience')


class ConfusionMatrix(TrivialExtendedDataFrame):
	"""
	A wrapper around a confusion matrix as a Pandas DataFrame.
	The rows are the correct labels, and the columns are the predicted labels.
	"""

	def __init__(self, data=None, index=None, columns=None, dtype=None, copy=False):
		super(BaseExtendedDataFrame, self).__init__(data=data, index=index, columns=columns, dtype=dtype, copy=copy)

	def warn_if_asymmetric(self) -> None:
		if self.rows != self.cols:
			logger.warning("Rows {} != columns {}".format(self.rows, self.columns))

	def is_symmetric(self) -> bool:
		return self.rows == self.cols

	def _repr_html_(self) -> str:
		return "<strong>{}: {} {}</strong>\n{}".format(
			self.__class__.__name__,
			self._dims(),
			Chars.check if self.rows==self.cols else Chars.x,
			pd.DataFrame._repr_html_(self), len(self)
		)

	def sub(self, names: Set[str]) -> ConfusionMatrix:
		return ConfusionMatrix(self.loc[names][names])

	def shuffle(self) -> ConfusionMatrix:
		"""
		Returns a copy with every value mapped to a new location.
		Destroys the correct links between labels and values.
		Useful for permutation tests.
		:return: A copy
		"""
		cp = deepcopy(self.flatten())
		np.random.shuffle(cp)
		vals = cp.reshape((len(self.rows), len(self.columns)))
		return ConfusionMatrix(vals, index=self.rows, columns=self.columns)

	def diagonals(self) -> np.array:
		return np.array([self.iat[i, i] for i in range(len(self))])

	def off_diagonals_quantiles(self, q: float = 0.5) -> np.array:
		lst = []
		for i in range(len(self)):
			lst.append(np.quantile([self.iat[i,j] for j in range(len(self))], q))
		return np.array(lst)

	def off_diagonals_means(self) -> np.array:
		lst = []
		for i in range(len(self)):
			lst.append(np.mean([self.iat[i,j] for j in range(len(self))]))
		return np.array(lst)

	def flatten(self) -> np.array:
		return self.values.flatten()

	def sum_diagonal(self) -> float:
		s = 0
		for i in range(len(self)):
			s += self.iat[i, i]
		return s

	def sum_off_diagonal(self) -> float:
		s = 0
		for i in range(len(self)):
			for j in range(len(self)):
				if i != j:
					s += self.iat[i, j]
		return s

	def score_df(self) -> pd.DataFrame:
		"""
		Get the diagonal elements as a Pandas DataFrame with columns 'name' and 'score'.
		:return: A Pandas DataFrame
		"""
		sers = []
		for score, name in self.scores():
			sers.append(pd.Series({'name': name, 'score': score}))
		return pd.DataFrame(sers)

	def symmetrize(self) -> ConfusionMatrix:
		"""Averages with its transpose, forcing it to be symmetric. Returns a copy."""
		return ConfusionMatrix(0.5 * (self + self.T))

	def triagonalize(self) -> ConfusionMatrix:
		"""
		NaNs out the upper triangle, returning a copy.
		You may consider calling symmetrize first.
		WARNING: Do NOT call a sorting method after this.
		"""
		return ConfusionMatrix(self.where(np.tril(np.ones(self.shape)).astype(np.bool)))

	def log(self) -> ConfusionMatrix:
		"""Takes the log10 of every value in this ConfusionMatrix, returning a new one."""
		return ConfusionMatrix(self.applymap(np.log10))

	def negative(self) -> ConfusionMatrix:
		return ConfusionMatrix(self.applymap(lambda x: -x))

	def sort(self, **kwargs) -> ConfusionMatrix:
		"""
		Sorts this confusion matrix to show clustering. The same ordering is applied to the rows and columns.
		Call this first. Do not call symmetrize(), log(), or triagonalize() before calling this.
		Returns a copy.
		:param: kwargs Passed to simulated_annealing: `steps`, `cooling_factor`, `temp`, `deterministic`
		:return: A dictionary mapping class names to their new positions (starting at 0)
		:return: A new ConfusionMatrix, sorted
		"""
		permutation = self.permutation(**kwargs)
		return self.sort_with(permutation)

	def permutation(self, **kwargs) -> Mapping[str, int]:
		"""
		Sorts this confusion matrix to show clustering. The same ordering is applied to the rows and columns.
		Returns the sorting. Does not alter this ConfusionMatrix.
		:param: kwargs Passed to simulated_annealing: `steps`, `cooling_factor`, `temp`, `deterministic`
		:return: A dictionary mapping class names to their new positions (starting at 0)
		"""
		if not self.is_symmetric():
			raise AmbiguousRequestError("Unclear how to sort because rows {} and columns {} differ".format(self.rows, self.columns))
		optimized = simulated_annealing(self.values, **kwargs)
		perm = list(reversed(optimized['perm']))
		perm = {name: perm.index(i) for i, name in enumerate(self.rows)}
		logger.info("Permutation for rows {}: {}".format(self.rows, perm))
		return perm

	def unsort(self) -> ConfusionMatrix:
		"""
		Sort by the labels alphabetically.
		"""
		labels = sorted(self.rows)
		return self.sort_first(labels)

	def sort_with(self, permutation: Union[Sequence[str], Mapping[str, int]]) -> ConfusionMatrix:
		"""
		Sorts this ConfusionMatrix's rows and columns by a predefined ordering. Returns a copy.
		:param permutation: Maps names (strings) to their 0-indexed positions (integers)
				If a mapping, takes as-is; these are returned by permutation()
				If a DataFrame, must have 2 columns 'key' (name) and 'value' (position), and 1 row per name
				If a str, tries to read a CSV file at that path into a DataFrame; uses Tools.csv_to_dict
		:return: A new ConfusionMatrix with sorted rows and columns
		"""
		if not self.is_symmetric():
			raise AmbiguousRequestError("Unclear how to sort because rows {} and columns {} differ".format(self.rows, self.columns))
		if isinstance(permutation, Sequence):
			if set(permutation) != set(self.rows):
				permutation = {name: i for i, name in enumerate(permutation)}
			else:
				raise RefusingRequestError("{} permutation elements instead of {}. See `sort_first`.".format(len(permutation), len(self)))
		data = self.reindex(sorted(self.rows, key=lambda s: permutation[s]), axis=1)
		xx = [permutation[name] for name in self.rows]
		data['__sort'] = xx
		data = data.sort_values('__sort').drop('__sort', axis=1)
		return ConfusionMatrix(data)

	def sort_first(self, first: Sequence[str]) -> ConfusionMatrix:
		first = [*first, *[r for r in self.rows if r not in first]]
		permutation = {name: i for i, name in enumerate(first)}
		return self.sort_with(permutation)

	@property
	def rows(self):
		return self.index.tolist()

	@property
	def cols(self):
		return self.columns.tolist()

	@property
	def length(self) -> int:
		"""Get a safe length, verifying that the len(rows) == len(cols)."""
		if len(self.rows) != len(self.cols):
			raise LengthMismatchError("{} rows != {} cols".format(len(self.rows), len(self.cols)))
		return len(self.rows)

	def __repr__(self) -> str:
		return "ConfusionMatrix({} labels @ {})".format(len(self.rows), hex(id(self)))

	def __str__(self) -> str:
		return repr(self)

	@classmethod
	def read_csv(cls, path: PathLike, *args, **kwargs):
		path = Path(path)
		df = pd.read_csv(path, index_col=0)
		df.index.name = 'name'
		return ConfusionMatrix(df)


class ConfusionMatrices:

	@classmethod
	def average(cls, matrices: Sequence[ConfusionMatrix]) -> ConfusionMatrix:
		"""
		Averages a list of confusion matrices.
		:param matrices: An iterable of ConfusionMatrices (does not need to be a list)
		:return: A new ConfusionMatrix
		"""
		if len(matrices) < 1:
			raise EmptyCollectionError("Cannot average 0 matrices")
		matrices = [m.unsort() for m in matrices]
		rows, cols, mx0 = matrices[0].rows, matrices[0].columns, matrices[0]
		if any((not m.is_symmetric() for m in matrices)):
			raise RefusingRequestError("Refusing to average matrices because for at least one matrix the rows and columns are different")
		for m in matrices[1:]:
			if m.rows != rows:
				raise RefusingRequestError("At least one confusion matrix has different rows than another (or different columns than another)")
			mx0 += m
		# noinspection PyTypeChecker
		return ConfusionMatrix((1.0 / len(matrices)) * mx0)

	@classmethod
	def agg_matrices(cls, matrices: Sequence[ConfusionMatrix], aggregation: Callable[[Sequence[pd.DataFrame]], None]) -> ConfusionMatrix:
		"""
		Averages a list of confusion matrices.
		:param matrices: An iterable of ConfusionMatrices (does not need to be a list)
		:param aggregation to perform, such as np.mean
		:return: A new ConfusionMatrix
		"""
		if len(matrices) < 1:
			raise EmptyCollectionError("Cannot aggregate 0 matrices")
		matrices = [mx.unsort() for mx in matrices]
		rows, cols, mx = matrices[0].rows, matrices[0].columns, matrices[0]
		if rows != cols:
			raise RefusingRequestError("Refusing to aggregate matrices because for at least one matrix the rows and columns are different")
		ms = []
		for m in matrices[1:]:
			if m.rows != rows or m.columns != cols:
				raise RefusingRequestError("At least one confusion matrix has different rows than another (or different columns than another)")
			ms.append(m)
		return ConfusionMatrix(aggregation(ms))

	@classmethod
	def zeros(cls, classes: Sequence[str]) -> ConfusionMatrix:
		return ConfusionMatrix(pd.DataFrame([
			pd.Series({'class': r, **{c: 0.0 for c in classes}})
			for r in classes
		]).set_index('class'))

	@classmethod
	def perfect(cls, classes: Sequence[str]) -> ConfusionMatrix:
		return ConfusionMatrix(pd.DataFrame([
			pd.Series({'class': r, **{c: 1.0 if r == c else 0.0 for c in classes}})
			for r in classes
		]).set_index('class'))

	@classmethod
	def uniform(cls, classes: Sequence[str]) -> ConfusionMatrix:
		return ConfusionMatrix(pd.DataFrame([
			pd.Series({'class': r, **{c: 1.0 / len(classes) for c in classes}})
			for r in classes
		]).set_index('class'))


__all__ = ['ConfusionMatrix', 'ConfusionMatrices']
