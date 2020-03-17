from typing import SupportsFloat, SupportsInt, TypeVar, Optional
import numpy as np
from dscience.tools.base_tools import BaseTools
V = TypeVar('V')


class NumericTools(BaseTools):

	@classmethod
	def fnone(cls, f: Optional[SupportsFloat]) -> float:
		return None if f is None else float(f)

	@classmethod
	def iroundopt(cls, f: Optional[SupportsInt]) -> int:
		# noinspection PyTypeChecker
		return None if f is None else int(np.round(f))

	@classmethod
	def iceilopt(cls, f: Optional[SupportsInt]) -> int:
		# noinspection PyTypeChecker
		return None if f is None else int(np.ceil(f))

	@classmethod
	def iflooropt(cls, f: Optional[SupportsInt]) -> int:
		# noinspection PyTypeChecker
		return None if f is None else int(np.floor(f))

	@classmethod
	def iround(cls, f: Optional[SupportsInt]) -> int:
		# noinspection PyTypeChecker
		return None if f is None else int(np.round(f))

	@classmethod
	def iceil(cls, f: SupportsFloat) -> int:
		"""
		Fixes np.ceil to return an Python integer rather than a Numpy float.
		:param f: A Python or Numpy float, or something else that defines __float__
		:return: An integer of the ceiling
		"""
		# noinspection PyTypeChecker
		return int(np.ceil(f))

	@classmethod
	def ifloor(cls, f: SupportsFloat) -> int:
		"""
		Fixes np.floor to return an Python integer rather than a Numpy float.
		:param f: A Python or Numpy float, or something else that defines __float__
		:return: An integer of the ceiling
		"""
		# noinspection PyTypeChecker
		return int(np.floor(f))

	@classmethod
	def imin(cls, *f):
		return int(np.min(f))

	@classmethod
	def imax(cls, *f):
		return int(np.max(f))

	@classmethod
	def slice_bounded(cls, arr: np.array, i: Optional[int], j: Optional[int]) -> np.array:
		"""
		Slices `arr[max(i,0), min(j, len(arr))`.
		Converts `i` and `j` to int.
		"""
		if i is None: i = 0
		if j is None: j = len(arr)
		if i < 0: i = len(arr) - i
		if j < 0: j = len(arr) - j
		start, stop = NumericTools.imax(0, i), NumericTools.imin(len(arr), j)
		return arr[start : stop]


__all__ = ['NumericTools']
