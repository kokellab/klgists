from typing import Callable, Any
import hashlib
import os
import codecs
import gzip

from klgists.common.exceptions import HashValidationFailedException, NoSuchFileException


class FileHasher:

	def __init__(self, algorithm: Callable[[], Any]=hashlib.sha1, extension: str='.sha1', buffer_size: int = 16*1024):
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
			hash_str = f.read().split()[0] # check only the first thing on the line before any spaces
			return hash_str == self.hashsum(file_name)

	def check_and_open(self, file_name: str, *args):
		return self._o(file_name, opener=lambda f: codecs.open(f, encoding='utf-8'), *args)

	def check_and_open_gzip(self, file_name: str, *args):
		return self._o(file_name, opener=gzip.open, *args)

	def _o(self, file_name: str, opener, *args):
		if not os.path.isfile(file_name + self.extension):
			raise NoSuchFileException("Hash for file {} does not exist".format(file_name))
		with open(file_name + self.extension, 'r', encoding="utf8") as f:
			if f.read() != self.hashsum(file_name):
				raise HashValidationFailedException("Hash for file {} does not match".format(file_name))
		return opener(file_name, *args)
