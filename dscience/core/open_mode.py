
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


__all__ = ['OpenMode']
