from __future__ import annotations
import logging
from typing import Sequence, Iterable, TypeVar, Union, Callable, Optional
import operator
import contextlib
from dscience.core import PathLike
from dscience.core.io import *
T = TypeVar('T', covariant=True)
Y = TypeVar('Y')
Z = TypeVar('Z')
logger = logging.getLogger('dscience')


class Pretty:
	@classmethod
	def condensed(cls, item, depth = 1):
		if isinstance(item, dict):
			return '{\n' + '\n'.join([
				'\t'*(depth+1) + k + ' = ' + cls.condensed(v, depth+1) for k, v in item.items()
			]) + '\n' + '\t'*depth + '}'
		else:
			return str(item)

	@classmethod
	def expanded(cls, item, depth = 1):
		if isinstance(item, dict):
			return '{\n' + '\n'.join([
				'\t'*(depth+1) + k + ' = ' + cls.expanded(v, depth+1) for k, v in item.items()
			]) + '\n' + '\t'*depth + '}'
		elif isinstance(item, (list, set)):
			return '[\n' + '\n'.join([
				'\t'*(depth+1) + cls.expanded(v, depth+1) for v in item
			]) + '\n' + '\t'*depth + ']'
		else:
			return str(item)


def nicesize(nbytes: int, space: str = '') -> str:
	"""
	Uses IEC 1998 units, such as KiB (1024).
	:param nbytes: Number of bytes
	:param space: Separator between digits and units
	:return: Formatted string
	"""
	data = {
		'PiB': 1024**5,
		'TiB': 1024**4,
		'GiB': 1024**3,
		'MiB': 1024**2,
		'KiB': 1024**1
	}
	for suffix, scale in data.items():
		if nbytes >= scale:
			break
	else:
		scale, suffix = 1, 'B'
	return str(nbytes // scale) + space + suffix


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

def null_context():
	yield

@contextlib.contextmanager
def silenced(no_stdout: bool = True, no_stderr: bool = True):
	with contextlib.redirect_stdout(DevNull()) if no_stdout else null_context():
		with contextlib.redirect_stderr(DevNull()) if no_stderr else null_context():
			yield


__all__ = ['nicesize', 'frozenlist', 'PathLike', 'Writeable', 'DevNull', 'LogWriter', 'DelegatingWriter', 'Capture', 'look', 'silenced', 'logger', 'Pretty']
