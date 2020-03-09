from typing import Any
from dscience.core.tiny import look as _look

class OptRow:
	"""
	Short for 'optional row'.
	A wrapper around a NamedTuple that returns None if the key doesn't exist.
	This is intended for Pandas itertuples().
	"""
	def __init__(self, row):
		self._row = row

	def __getattr__(self, item: str) -> Any:
		try:
			return getattr(self._row, item)
		except AttributeError:
			return None

	def opt(self, item: str, look=None) -> Any:
		x = getattr(self, item)
		if x is None: return None
		return _look(x, look)

	def req(self, item: str, look=None) -> Any:
		x = getattr(self._row, item)
		if x is None: return None
		return _look(x, look)

	def __contains__(self, item):
		try:
			getattr(self._row, item)
			return True
		except AttributeError:
			return False

	def items(self):
		# noinspection PyProtectedMember
		return self._row._asdict()

	def keys(self):
		# noinspection PyProtectedMember
		return self._row._asdict().keys()

	def values(self):
		# noinspection PyProtectedMember
		return self._row._asdict().values()

	def __repr__(self):
		return self.__class__.__name__ + '@' + hex(id(self))

	def __str__(self):
		return self.__class__.__name__

	def __eq__(self, other):
		# noinspection PyProtectedMember
		return self._row == other._row

__all__ = ['OptRow']
