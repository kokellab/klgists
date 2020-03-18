from __future__ import annotations
import logging
from typing import TypeVar, Union, Any
import abc
import contextlib
# noinspection PyUnresolvedReferences
from dscience.core import PathLike
T = TypeVar('T', covariant=True)
Y = TypeVar('Y')
Z = TypeVar('Z')
logger = logging.getLogger('dscience')


class Writeable(metaclass=abc.ABCMeta):

	@classmethod
	def isinstance(cls, value: Any):
		return hasattr(value, 'write') and hasattr(value, 'flush') and hasattr(value, 'close')

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
	def split(self, x: str): return self.__cio.getvalue().split(x)


class OpenMode(str):
	"""
	Extended file open modes with a superset of meanings.
	The underlying string contains a Python open()-compatible string.
		- 'r' means read
		- 'w' and 'o' both mean overwrite
		- 'a' means append
		- 's' means "safe" -- complain if it exists (neither overwrite nor append)
		- 'b' means binary
		- 'z' means compressed with gzip; works in both binary and text modes
		- 'd' means detect gzip
	"""

	# noinspection PyMissingConstructor
	def __init__(self, mode: str):
		self._raw = mode.replace('w', 'o')
		self.internal = self.__strip()
	def __repr__(self): return self.internal
	def __str__(self): return self.internal
	def __strip(self):
		return self._raw.replace('o', 'w').replace('s', 'w').replace('z', '').replace('i', '').replace('d', '')
	@property
	def read(self) -> bool: return 'r' in self._raw
	@property
	def write(self) -> bool: return 'r' not in self._raw
	@property
	def safe(self) -> bool: return 's' in self._raw
	@property
	def overwrite(self) -> bool: return 'o' in self._raw or 'w' in self._raw
	@property
	def ignore(self) -> bool: return 'i' in self._raw
	@property
	def append(self) -> bool: return 'a' in self._raw
	@property
	def text(self) -> bool: return 'b' not in self._raw
	@property
	def binary(self) -> bool: return 'b' in self._raw
	@property
	def gzipped(self) -> bool: return 'z' in self._raw

	def __eq__(self, other):
		return str(self).replace('w', 'o') == str(other).replace('w', 'o')


def null_context():
	yield

@contextlib.contextmanager
def silenced(no_stdout: bool = True, no_stderr: bool = True):
	with contextlib.redirect_stdout(DevNull()) if no_stdout else null_context():
		with contextlib.redirect_stderr(DevNull()) if no_stderr else null_context():
			yield


__all__ = ['Writeable', 'DevNull', 'LogWriter', 'DelegatingWriter', 'Capture', 'OpenMode', 'PathLike']

