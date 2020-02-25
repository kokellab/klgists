from typing import SupportsBytes, Sequence, Mapping, Iterable, Any, Union, Optional, Generator
from pathlib import PurePath
import os, tempfile
from pathlib import Path
import re
import gzip, json, hashlib
from contextlib import contextmanager
import logging
from dscience_gists.core.json_encoder import JsonEncoder
from dscience_gists.core import Writeable, PathLike
from dscience_gists.core.exceptions import ParsingError, BadCommandError, InvalidDirectoryError, InvalidFileError
from dscience_gists.core.open_mode import *
from dscience_gists.tools.common_tools import VeryCommonTools
logger = logging.getLogger('dscience_gists')
COMPRESS_LEVEL = 9
ENCODING = 'utf8'

try:
	import jsonpickle
	import jsonpickle.ext.numpy as jsonpickle_numpy
	jsonpickle_numpy.register_handlers()
	import jsonpickle.ext.pandas as jsonpickle_pandas
	jsonpickle_pandas.register_handlers()
except ImportError:
	# zero them all out
	jsonpickle, jsonpickle_numpy, jsonpickle_pandas = None, None, None
	logger.error("Could not import jsonpickle")


class FilesysTools(VeryCommonTools):

	@classmethod
	def updir(cls, n: int, *parts) -> Path:
		"""
		Get an absolute path `n` parents from `os.getcwd()`.
		Ex: In dir '/home/john/dir_a/dir_b':
			`updir(2, 'dir1', 'dir2')  # returns Path('/home/john/dir1/dir2')`
		Does not sanitize.
		"""
		base = Path(os.getcwd())
		for _ in range(n):
			base = base.parent
		for part in parts:
			base = base / part
		return base.resolve()

	@classmethod
	def try_cleanup(cls, path: Path) -> None:
		"""
		Try to delete a file (probably temp file), if it exists, and log any PermissionError.
		"""
		path = Path(path)
		if path.exists():
			try:
				path.unlink()
			except PermissionError:
				logger.error("Permission error preventing deleting {}".format(path))

	@classmethod
	def read_lines_file(cls, path: PathLike, ignore_comments: bool = False) -> Sequence[str]:
		"""
		Returns a list of lines in the file, optionally skipping lines starting with '#' or that only contain whitespace.
		"""
		lines = []
		with FilesysTools.open_file(path, 'r') as f:
			for line in f.readlines():
				line = line.strip()
				if not ignore_comments or not line.startswith('#') and not len(line.strip()) == 0:
					lines.append(line)
		return lines

	@classmethod
	def read_properties_file(cls, path: PathLike) -> Mapping[str, str]:
		"""
		Reads a .properties file, which is a list of lines with key=value pairs (with an equals sign).
		Lines beginning with # are ignored.
		Each line must contain exactly 1 equals sign.
		:param path: Read the file at this local path
		:return: A dict mapping keys to values, both with surrounding whitespace stripped
		"""
		dct = {}
		with FilesysTools.open_file(path, 'r') as f:
			for i, line in enumerate(f.readlines()):
				line = line.strip()
				if len(line) == 0 or line.startswith('#'): continue
				if line.count('=') != 1:
					raise ParsingError("Bad line {} in {}".format(i, path))
				k, v = line.split('=')
				if k.strip() in dct:
					raise ParsingError("Duplicate property {} (line {})".format(k.strip(), i))
				dct[k.strip()] = v.strip()
		return dct

	@classmethod
	def write_properties_file(cls, properties: Mapping[Any, Any], path: Union[str, PurePath], mode: str = 'o'):
		if not OpenMode(mode).write:
			raise BadCommandError("Cannot write text to {} in mode {}".format(path, mode))
		with FilesysTools.open_file(path, mode) as f:
			bads = []
			for k, v in properties.items():
				if '=' in k or '=' in v or '\n' in k or '\n' in v:
					bads.append(k)
				f.write(
					str(k).replace('=', '--').replace('\n', '\\n')
					+ '='
					+ str(v).replace('=', '--').replace('\n', '\\n')
					+ '\n'
				)
			if 0 < len(bads) <= 10:
				logger.warning("At least one properties entry contains an equals sign or newline (\\n). These were escaped: {}".format(', '.join(bads)))
			elif len(bads) > 0:
				logger.warning("At least one properties entry contains an equals sign or newline (\\n), which were escaped.")

	@classmethod
	def make_dirs(cls, s: PathLike) -> None:
		# '' can break on Windows
		if str(s) != '':
			Path(s).mkdir(exist_ok=True, parents=True)

	@classmethod
	def save_json(data, path: PathLike, mode: str = 'w') -> None:
		with FilesysTools.open_file(path, mode) as f:
			json.dump(data, f, ensure_ascii=False, cls=JsonEncoder)

	@classmethod
	def load_json(cls, path: PathLike):
		with FilesysTools.open_file(path, 'r') as f:
			return json.load(f)

	@classmethod
	def save_jsonpkl(cls, data, path: PathLike, mode: str = 'w') -> None:
		if jsonpickle is None:
			raise ImportError("No jsonpickle")
		FilesysTools.write_text(jsonpickle.encode(data), path, mode=mode)

	@classmethod
	def load_jsonpkl(cls, path: PathLike) -> dict:
		if jsonpickle is None:
			raise ImportError("No jsonpickle")
		return jsonpickle.decode(FilesysTools.read_text(path))

	@classmethod
	def read_bytes(cls, path: PathLike) -> bytes:
		with FilesysTools.open_file(path, 'rb') as f:
			return f.read()

	@classmethod
	def read_text(cls, path: PathLike) -> str:
		with FilesysTools.open_file(path, 'r') as f:
			return f.read()

	@classmethod
	def write_bytes(cls, data: Any, path: PathLike, mode: str = 'wb') -> None:
		if not OpenMode(mode).write or not OpenMode(mode).binary:
			raise BadCommandError("Cannot write bytes to {} in mode {}".format(path, mode))
		with FilesysTools.open_file(path, mode) as f:
			f.write(data)

	@classmethod
	def write_text(cls, data: Any, path: PathLike, mode: str = 'w'):
		if not OpenMode(mode).write or OpenMode(mode).binary:
			raise BadCommandError("Cannot write text to {} in mode {}".format(path, mode))
		with FilesysTools.open_file(path, mode) as f:
			f.write(str(data))

	@classmethod
	def prep_dir(cls, path: PathLike, exist_ok: bool) -> bool:
		"""
		Prepares a directory by making it if it doesn't exist.
		If exist_ok is False, calls logger.warning it already exists
		"""
		path = cls.sanitize_directory_path(path)
		exists = path.exists()
		# On some platforms we get generic exceptions like permissions errors, so these are better
		if exists and not path.is_dir():
			raise InvalidDirectoryError("Path {} exists but is not a file".format(path))
		if exists and not exist_ok:
			logger.warning("Directory {} already exists".format(path))
		if not exists:
			# NOTE! exist_ok in mkdir throws an error on Windows
			path.mkdir(parents=True)
		return exists

	@classmethod
	def prep_file(cls, path: PathLike, overwrite: bool = True, append: bool = False) -> bool:
		"""Prepares a file path by making its parent directory (if it doesn't exist) and checking it."""
		# On some platforms we get generic exceptions like permissions errors, so these are better
		# TODO handle ignore
		path = cls.sanitize_file_path(path)
		exists = path.exists()
		if overwrite and append:
			raise BadCommandError("Can't append and overwrite file {}".format(path))
		if exists and not overwrite and not append:
			raise FileExistsError("Path {} already exists".format(path))
		elif exists and not path.is_file() and not path.is_symlink():  # TODO check link?
			raise InvalidFileError("Path {} exists but is not a file".format(path))
		# NOTE! exist_ok in mkdir throws an error on Windows
		if not path.parent.exists():
			Path(path.parent).mkdir(parents=True, exist_ok=True)
		return exists

	@classmethod
	@contextmanager
	def open_file(cls, path: PathLike, mode: str):
		"""
		Opens a file in a safer way, always using the encoding set in Kale (utf8) by default.
		This avoids the problems of accidentally overwriting, forgetting to set mode, and not setting the encoding.
		Note that the default encoding on open() is not UTF on Windows.
		Raises specific informative errors.
		Cannot set overwrite in append mode.
		:param path:
		:param mode: See `OpenMode`
		"""
		path = Path(path)
		mode = OpenMode(mode)
		if mode.write and mode.safe and path.exists():
			raise InvalidFileError("Path {} already exists".format(path))
		if not mode.read:
			FilesysTools.prep_file(path, overwrite=mode.overwrite, append=mode.append)
		if mode.gzipped:
			yield gzip.open(path, mode.internal, compresslevel=COMPRESS_LEVEL)
		elif mode.binary:
			yield open(path, mode.internal)
		else:
			yield open(path, mode.internal, encoding=ENCODING)

	@classmethod
	def write_lines(cls, iterable: Iterable[Any], path: PathLike, mode: str = 'w') -> int:
		"""
		Just writes an iterable line-by-line to a file, using '\n'.
		Makes the parent directory if needed.
		Checks that the iterable is a "true iterable" (not a string or bytes).
		:return The number of lines written (the same as len(iterable) if iterable has a length)
		:raises FileExistsError If the path exists and append is False
		:raises PathIsNotFileError If append is True, and the path exists but is not a file
		"""
		path = Path(path)
		mode = OpenMode(mode)
		if not mode.overwrite or mode.binary:
			raise ValueError("Wrong mode for writing a text file: {}".format(mode))
		if not FilesysTools.is_true_iterable(iterable):
			raise ValueError("Not a true iterable")  # TODO include iterable if small
		FilesysTools.prep_file(path, mode.overwrite, mode.append)
		n = 0
		with FilesysTools.open_file(path, mode) as f:
			for x in iterable:
				f.write(str(x) + '\n')
			n += 1
		return n

	@classmethod
	def sha1(cls, x: SupportsBytes) -> str:
		return FilesysTools.hash_hex(x, hashlib.sha1)

	@classmethod
	def sha256(cls, x: SupportsBytes) -> str:
		return FilesysTools.hash_hex(x, hashlib.sha256)

	@classmethod
	def hash_hex(cls, x: SupportsBytes, algorithm: str) -> str:
		"""Return the hex-encoded hash of the object (converted to bytes)."""
		m = hashlib.new(algorithm)
		m.update(bytes(x))
		return m.hexdigest()

	@classmethod
	def replace_in_file(cls, path: str, changes: Mapping[str, str]) -> None:
		"""Uses re.sub repeatedly to modify (AND REPLACE) a file's content."""
		with open(path) as f: data = f.read()
		for key, value in changes.items():
			data = re.sub(key, value, data, re.MULTILINE, re.DOTALL)
		with open(path, 'w', encoding="utf8") as f: f.write(data)

	@classmethod
	def tmppath(cls, path: Optional[PathLike] = None, **kwargs) -> Generator[Path, None, None]:
		if path is None:
			path = tempfile.mktemp()
		try:
			yield Path(path, **kwargs)
		finally:
			Path(path).unlink()

	@classmethod
	def tmpfile(cls, path: Optional[PathLike] = None, spooled: bool = False, **kwargs) -> Generator[Writeable, None, None]:
		if spooled:
			with tempfile.SpooledTemporaryFile(**kwargs) as x:
				yield x
		elif path is None:
			with tempfile.TemporaryFile(**kwargs) as x:
				yield x
		else:
			with tempfile.NamedTemporaryFile(str(path), **kwargs) as x:
				yield x

	@classmethod
	def tmpdir(cls, **kwargs) -> Generator[Path, None, None]:
		with tempfile.TemporaryDirectory(**kwargs) as x:
			yield Path(x)



__all__ = ['FilesysTools']
