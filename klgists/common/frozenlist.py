from __future__ import annotations
from typing import Sequence, TypeVar, Iterable, overload


T = TypeVar('T', covariant=True)


class frozenlist(Sequence):
	"""
	An immutable sequence backed by a list.
	The sole advantage over a tuple is the list-like __str__ with square brackets, which may be less confusing to a user.
	"""
	def __init__(self, *items: Iterable[T]):
		self.__items = list(items)

	@overload
	def __getitem__(self, i: int) -> T:
		return self.__items[i]

	@overload
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


__all__ = ['frozenlist']
