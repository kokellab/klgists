from __future__ import annotations
import os
import logging
from typing import Sequence, Iterable, TypeVar, Union, Callable, Optional
import operator
from pathlib import PurePath
import abc
logger = logging.getLogger('dscience_gists')
PathLike = Union[str, PurePath, os.PathLike]
T = TypeVar('T', covariant=True)
Y = TypeVar('Y')
Z = TypeVar('Z')


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


class Writeable(metaclass=abc.ABCMeta):

	def write(self, msg):
		raise NotImplementedError()

	def flush(self):
		raise NotImplementedError()

	def close(self):
		raise NotImplementedError()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()


class DevNull(Writeable):
	"""Pretends to write but doesn't."""
	def write(self, msg): pass
	def flush(self): pass
	def close(self): pass

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()


class LogWriter:
	"""
	A call to a logger at some level, pretending to be a writer.
	Has a write method, as well as flush and close methods that do nothing.
	"""
	def __init__(self, level: Union[int, str]):
		if isinstance(level, str): level = level.upper()
		self.level = logging.getLevelName(level)

	def write(self, msg: str):
		getattr(logger, self.level)(msg)

	def flush(self): pass
	def close(self): pass

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()


class DelegatingWriter(object):
	# we CANNOT override TextIOBase: It causes hangs
	def __init__(self, *writers):
		self._writers = writers

	def write(self, s):
		for writer in self._writers:
			writer.write(s)

	def flush(self):
		for writer in self._writers:
			writer.flush()

	def close(self):
		for writer in self._writers:
			writer.close()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()


class Capture:
	"""
	A lazy string-like object that wraps around a StringIO result.
	It's too hard to fully subclass a string while keeping it lazy.
	"""
	def __init__(self, cio):
		self.__cio = cio
	@property
	def lines(self):
		return self.split('\n')
	@property
	def value(self):
		return self.__cio.getvalue()
	def __repr__(self): return self.__cio.getvalue()
	def __str__(self): return self.__cio.getvalue()
	def __len__(self): return len(repr(self))
	def split(self, x): return self.__cio.getvalue().split(x)


def look(obj: Y, attrs: Union[str, Iterable[str], Callable[[Y], Z]]) -> Optional[Z]:
	"""
	See VeryCommonTools.look.
	"""
	if attrs is None:
		return obj
	if not isinstance(attrs, str) and hasattr(attrs, '__len__') and len(attrs) == 0:
		return obj
	if isinstance(attrs, str):
		attrs = operator.attrgetter(attrs)
	elif isinstance(attrs, Iterable) and all((isinstance(a, str) for a in attrs)):
		attrs = operator.attrgetter('.'.join(attrs))
	elif not callable(attrs):
		raise TypeError(
			"Type {} unrecognized for key/attribute. Must be a function, a string, or a sequence of strings"
			.format(type(attrs)))
	try:
		return attrs(obj)
	except AttributeError:
		return None

__all__ = ['frozenlist', 'PathLike', 'Writeable', 'DevNull', 'LogWriter', 'DelegatingWriter', 'Capture', 'look']
