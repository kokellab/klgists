from klgists.common.tools import *
from klgists.common.tools.datatype_tools import *
from klgists.common.tools.unit_tools import *
from klgists.common.tools.sys_tools import *
from klgists.common.tools.timing_tools import *


class GistTools(
	CommonTools, StringTools, NumericTools, ConsoleTools, FilesysTools, IoTools,
	PandasTools, UnitTools, TimingTools, ProgramTools
	):
	"""
	A collection of utility static functions specific to kale but not to the specifics of data in Valar.
	Mostly provided for use outside of Kale, but can also be used by Kale code.
	"""

	from klgists.files.file_hasher import FileHasher as __klfh
	FileHasher = __klfh


class OptRow:
	"""
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
		return GistTools.look(x, look)

	def req(self, item: str, look=None) -> Any:
		x = getattr(self._row, item)
		if x is None: return None
		return GistTools.look(x, look)

	def __contains__(self, item):
		try:
			getattr(self._row, item)
			return True
		except AttributeError:
			return False

	def items(self):
		return self._row._asdict()

	def keys(self):
		return self._row._asdict().keys()

	def values(self):
		return self._row._asdict().values()

	def __repr__(self):
		return self.__class__.__name__ + '@' + hex(id(self))

	def __str__(self):
		return self.__class__.__name__

	def __eq__(self, other):
		return self._row == other._row


__all__ = ['GistTools', 'OptRow']
