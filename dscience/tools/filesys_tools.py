from typing import SupportsBytes, Sequence, Mapping, Iterable, Any, Union, Optional, Generator
from pathlib import PurePath, Path
import stat
import os, tempfile
from datetime import datetime
import re
import shutil
import os, platform, socket, sys
from getpass import getuser
import gzip, json, hashlib
from contextlib import contextmanager
import logging
import pandas as pd
from dscience.core.web_resource import *
from dscience.core import JsonEncoder
from dscience.core.io import Writeable, PathLike, OpenMode
from dscience.core.hasher import *
from dscience.core.exceptions import ParsingError, BadCommandError, FileDoesNotExistError, ContradictoryRequestError, AlreadyUsedError
from dscience.tools.base_tools import BaseTools
from dscience.tools.path_tools import PathTools
logger = logging.getLogger('dscience')
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


class FilesysTools(BaseTools):

	@classmethod
	def new_hasher(cls, algorithm: str = 'sha1'):
		return FileHasher(algorithm)

	@classmethod
	def new_webresource(cls, url: str, archive_member: Optional[str], local_path: PathLike) -> WebResource:
		return WebResource(url, archive_member, local_path)

	@classmethod
	def get_env_info(cls, extras: Optional[Mapping[str, Any]] = None) -> Mapping[str, str]:
		"""
		Get a dictionary of some system and environment information.
		Includes os_release, hostname, username, mem + disk, shell, etc.
		"""
		try:
			import psutil
			pdata = {
				'disk_used': psutil.disk_usage('.').used,
				'disk_free': psutil.disk_usage('.').free,
				'memory_used': psutil.virtual_memory().used,
				'memory_available': psutil.virtual_memory().available
			}
		except ImportError:
			psutil, pdata = None, {}
			logger.warning("Couldn't load psutil")
		if extras is None: extras = {}
		mains = {
			'os_release': platform.platform(),
			'hostname': socket.gethostname(),
			'username': getuser(),
			'python_version': sys.version,
			'shell': os.environ['SHELL'],
			'environment_info_capture_datetime': datetime.now().isoformat(),
			**psutil
		}
		return {k: str(v) for k, v in {**mains, **extras}.items()}

	@classmethod
	def delete_surefire(cls, path: PathLike) -> Optional[Exception]:
		"""
		Deletes files or directories cross-platform, but working around multiple issues in Windows.
		:return Returns None, or an Exception for minor warnings
		:raises IOError If it can't delete
		"""
		# we need this because of Windows
		path = str(path)
		logger.debug("Permanently deleting {} ...".format(path))
		chmod_err = None
		try:
			os.chmod(path, stat.S_IRWXU)
		except Exception as e:
			chmod_err = e
		# another reason for returning exception:
		# We don't want to interrupt the current line being printed like in slow_delete
		if os.path.isdir(path):
			shutil.rmtree(path, ignore_errors=True)  # ignore_errors because of Windows
			try:
				os.remove(path)  # again, because of Windows
			except IOError:
				pass  # almost definitely because it doesn't exist
		else:
			os.remove(path)
		logger.debug("Permanently deleted {}".format(path))
		return chmod_err

	@classmethod
	def trash(cls, path: PathLike, trash_dir: PathLike = Path):
		logger.debug("Trashing {} to {} ...".format(path, trash_dir))
		shutil.move(str(path), str(trash_dir))
		logger.debug("Trashed {} to {}".format(path, trash_dir))

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
				k, v = k.strip(), v.strip()
				if k in dct:
					raise AlreadyUsedError("Duplicate property {} (line {})".format(k, i), key=k)
				dct[k] = v
		return dct

	@classmethod
	def write_properties_file(cls, properties: Mapping[Any, Any], path: Union[str, PurePath], mode: str = 'o'):
		if not OpenMode(mode).write:
			raise ContradictoryRequestError("Cannot write text to {} in mode {}".format(path, mode))
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
		"""
		Make a directory (ok if exists, will make parents).
		Avoids a bug on Windows where the path '' breaks. Just doesn't make the path '' (assumes it means '.').
		"""
		# '' can break on Windows
		if str(s) != '':
			Path(s).mkdir(exist_ok=True, parents=True)

	@classmethod
	def save_json(cls, data, path: PathLike, mode: str = 'w') -> None:
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

	@staticmethod
	def read_any(path: PathLike) -> Union[str, bytes, Sequence[str], pd.DataFrame, Sequence[int], Sequence[float], Sequence[str], Mapping[str, str]]:
		"""
		Reads a variety of simple formats based on filename extension, including '.txt', 'csv', .xml', '.properties', '.json'.
		Also reads '.data' (binary), '.lines' (text lines).
		And formatted lists: '.strings', '.floats', and '.ints' (ex: "[1, 2, 3]").
		:param path:
		:return:
		"""
		path = Path(path)
		ext = path.suffix.lstrip('.')
		def load_list(dtype):
			return [dtype(s) for s in FilesysTools.read_lines_file(path)[0].replace(' ', '').replace('[', '').replace(']', '').split(',')]
		if ext == 'lines':
			return FilesysTools.read_lines_file(path)
		elif ext == 'txt':
			return path.read_text('utf-8')
		elif ext == 'data':
			return path.read_bytes()
		elif ext == 'json':
			return FilesysTools.load_json(path)
		elif ext == 'properties':
			return FilesysTools.read_properties_file(path)
		elif ext == 'csv':
			return pd.read_csv(path)
		elif ext == 'ints':
			return load_list(int)
		elif ext == 'floats':
			return load_list(float)
		elif ext == 'strings':
			return load_list(str)
		elif ext == 'xml':
			from xml.etree import ElementTree
			ElementTree.parse(path).getroot()
		else:
			raise TypeError("Did not recognize resource file type for file {}".format(path))

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
			raise FileDoesNotExistError("Path {} already exists".format(path))
		if not mode.read:
			PathTools.prep_file(path, overwrite=mode.overwrite, append=mode.append)
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
			raise ContradictoryRequestError("Wrong mode for writing a text file: {}".format(mode))
		if not FilesysTools.is_true_iterable(iterable):
			raise TypeError("Not a true iterable")  # TODO include iterable if small
		PathTools.prep_file(path, mode.overwrite, mode.append)
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
		"""
		Return the hex-encoded hash of the object (converted to bytes).
		"""
		m = hashlib.new(algorithm)
		m.update(bytes(x))
		return m.hexdigest()

	@classmethod
	def replace_in_file(cls, path: str, changes: Mapping[str, str]) -> None:
		"""
		Uses re.sub repeatedly to modify (AND REPLACE) a file's content.
		"""
		with open(path) as f: data = f.read()
		for key, value in changes.items():
			data = re.sub(key, value, data, re.MULTILINE, re.DOTALL)
		with open(path, 'w', encoding="utf8") as f: f.write(data)

	@classmethod
	def tmppath(cls, path: Optional[PathLike] = None, **kwargs) -> Generator[Path, None, None]:
		"""
		Makes a temporary Path. Won't create `path` but will delete it at the end.
		If `path` is None, will use `tempfile.mktemp`.
		"""
		if path is None:
			path = tempfile.mktemp()
		try:
			yield Path(path, **kwargs)
		finally:
			Path(path).unlink()

	@classmethod
	def tmpfile(cls, path: Optional[PathLike] = None, spooled: bool = False, **kwargs) -> Generator[Writeable, None, None]:
		"""
		Simple wrapper around tempfile.TemporaryFile, tempfile.NamedTemporaryFile, and tempfile.SpooledTemporaryFile.
		:param path:
		:param spooled:
		:param kwargs:
		:return:
		"""
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
