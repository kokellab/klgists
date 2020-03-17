from __future__ import annotations
import os
import logging
from typing import Sequence, Iterable, TypeVar, Union
from pathlib import PurePath
from dscience.core.exceptions import ImmutableError
T = TypeVar('T', covariant=True)
logger = logging.getLogger('dscience')

PathLike = Union[str, PurePath, os.PathLike]
def pathlike_isinstance(value):
	return isinstance(value, str) or isinstance(value, os.PathLike) or isinstance(value, PurePath)
PathLike.isinstance = pathlike_isinstance

# noinspection PyPep8Naming
class frozenlist(Sequence):
	"""
	An immutable sequence backed by a list.
	The sole advantage over a tuple is the list-like __str__ with square brackets, which may be less confusing to a user.
	"""
	def __init__(self, items: Iterable[T]):
		self.__items = list(items)

	def __getitem__(self, item) -> T:
		if isinstance(item, int):
			return self.__items[item]
		else:
			return frozenlist(self.__items[item])

	def __setitem__(self, key, value):
		raise ImmutableError()

	def __len__(self) -> int:
		return len(self.__items)

	def __repr__(self):
		return repr(self.__items)

	def __eq__(self, other):
		return type(self) == type(other) and self.__items == other.__items

	def __str__(self):
		return repr(self.__items)


__version__ = '0.1.0'
__all__ = ['frozenlist', 'PathLike']
