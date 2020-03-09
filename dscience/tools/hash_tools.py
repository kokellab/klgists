from typing import Callable, Any
import hashlib
import os
import codecs
import gzip
from dscience.core.exceptions import InvalidFileError
from dscience.core.exceptions import HashValidationFailedError
from dscience.tools.base_tools import BaseTools


class FileHasher:
	"""
	Makes and reads .sha1 / .sha256 files next to existing paths.
	"""

	def __init__(self, algorithm: Callable[[], Any] = hashlib.sha1, extension: str = '.sha1', buffer_size: int = 16*1024):
		self.algorithm = algorithm
		self.extension = extension
		self.buffer_size = buffer_size

	def hashsum(self, file_name: str) -> str:
		alg = self.algorithm()
		with open(file_name, 'rb') as f:
			for chunk in iter(lambda: f.read(self.buffer_size), b''):
				alg.update(chunk)
		return alg.hexdigest()

	def add_hash(self, file_name: str) -> None:
		with open(file_name + self.extension, 'w', encoding="utf8") as f:
			s = self.hashsum(file_name)
			f.write(s)

	def check_hash(self, file_name: str) -> bool:
		if not os.path.isfile(file_name + self.extension): return False 
		with open(file_name + self.extension, 'r', encoding="utf8") as f:
			hash_str = f.read().split()[0]  # check only the first thing on the line before any spaces
			return hash_str == self.hashsum(file_name)

	def check_and_open(self, file_name: str, *args):
		return self._o(file_name, opener=lambda f: codecs.open(f, encoding='utf-8'), *args)

	def check_and_open_gzip(self, file_name: str, *args):
		return self._o(file_name, opener=gzip.open, *args)

	def _o(self, file_name: str, opener, *args):
		if not os.path.isfile(file_name + self.extension):
			raise InvalidFileError("Hash for file {} does not exist".format(file_name))
		with open(file_name + self.extension, 'r', encoding="utf8") as f:
			exp, act = f.read(), self.hashsum(file_name)
			if exp != act:
				raise HashValidationFailedError("Hash for file {} does not match".format(file_name), key=file_name, expected=exp, actual=act)
		return opener(file_name, *args)


class HashTools(BaseTools):

	@classmethod
	def new_hasher(cls, algorithm: Callable[[], Any] = hashlib.sha1, extension: str = '.sha1', buffer_size: int = 16*1024):
		return FileHasher(algorithm, extension, buffer_size)


__all__ = ['FileHasher', 'HashTools', 'HashValidationFailedError']


