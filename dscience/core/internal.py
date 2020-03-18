from __future__ import annotations
import logging
import os
from pathlib import PurePath
from typing import Iterable, TypeVar, Union, Callable, Optional
import operator
import contextlib
T = TypeVar('T', covariant=True)
Y = TypeVar('Y')
Z = TypeVar('Z')
logger = logging.getLogger('dscience')

PathLike = Union[str, PurePath, os.PathLike]
def pathlike_isinstance(value):
	return isinstance(value, str) or isinstance(value, os.PathLike) or isinstance(value, PurePath)
PathLike.isinstance = pathlike_isinstance


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


__all__ = ['nicesize', 'look', 'logger', 'Pretty']
