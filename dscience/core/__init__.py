from __future__ import annotations
import os
import logging
from typing import Sequence, Iterable, TypeVar, Union
from pathlib import PurePath
PathLike = Union[str, PurePath, os.PathLike]
T = TypeVar('T', covariant=True)
logger = logging.getLogger('dscience')


# noinspection PyPep8Naming
class frozenlist(Sequence):
	"""
	An immutable sequence backed by a list.
	The sole advantage over a tuple is the list-like __str__ with square brackets, which may be less confusing to a user.
	"""
	def __init__(self, *items: Iterable[T]):
		self.__items = list(items)

	def __getitem__(self, i: int) -> T:
		return self.__items[i]

	def __getitem__(self, s: slice) -> frozenlist[T]:
		return frozenlist(self.__items[s])

	def __getitem__(self, item) -> T:
		if isinstance(item, slice):
			return self[item]
		else:
			return self[item]

	def __len__(self) -> int:
		return len(self.__items)

	def __repr__(self):
		return repr(self.__items)

	def __str__(self):
		return repr(self.__items)


__version__ = '0.1.0'
__all__ = ['frozenlist', 'PathLike']
