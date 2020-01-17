from klgists.common.tools import *
from klgists.common.chars import *
from klgists.common.exceptions import ParsingError, BadCommandError, InvalidDirectoryException, InvalidFileException
from klgists.files.path_sanitization import WindowsPaths
from copy import copy
from textwrap import wrap, indent
from typing import SupportsBytes

import contextlib
import subprocess
import gzip
import hashlib

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


class ConsoleTools(VeryCommonTools):

	CURSOR_UP_ONE = '\x1b[1A'
	ERASE_LINE = '\x1b[2K'

	@staticmethod
	def confirm(msg: Union[None, str, Callable[[], None]] = None) -> bool:
		"""
		Asks for a confirmation from the user using the bulliten input().
		:param msg: If None defaults to 'Confirm? [yes/no]'
		:return: True if the user answered 'yes'; False otherwise
		"""
		if msg is None: msg = "Confirm? [yes/no]"
		if isinstance(msg, str):
			msg = lambda: print(msg + ' ', end='')
		while True:
			msg()
			# TODO silence output; for some reason Tools.silenced doesn't work
			command = input('')
			if command.lower() == '/exit': break
			if command.lower() in ['yes', 'y']: return True
			elif command.lower() in ['no', 'n']: return False

	@staticmethod
	def clear_line(n: int = 1) -> None:
		"""
		Writes control characters to stdout to delete the previous line and move the curser up.
		This only works in a shell.
		:param n: The number of lines to erase
		"""
		for _ in range(n):
			sys.stdout.write(ConsoleTools.CURSOR_UP_ONE)
			sys.stdout.write(ConsoleTools.ERASE_LINE)


class IoTools(VeryCommonTools):

	@staticmethod
	@contextmanager
	def silenced(no_stdout:bool=True, no_stderr:bool=True):
		with contextlib.redirect_stdout(DevNull()) if no_stdout else IoTools.null_context():
			with contextlib.redirect_stderr(DevNull()) if no_stderr else IoTools.null_context():
				yield

	@staticmethod
	def call_cmd(*cmd: str, **kwargs) -> subprocess.CompletedProcess:
		"""
		Calls subprocess.run with capture_output=True, and logs a debug statement with the command beforehand.
		:param cmd: A sequence to call
		:param kwargs: Passed to subprocess.run
		"""
		logger.debug("Calling '{}'".format(' '.join(cmd)))
		return subprocess.run(*[str(c) for c in cmd], capture_output=True, check=True, **kwargs)

	@staticmethod
	def call_cmd_utf(*cmd: str, log_fn: Callable[[str], None] = logger.error, **kwargs) -> subprocess.CompletedProcess:
		"""
		Like `call_cmd`, but sets `text=True` and `encoding=utf8`, and strips stdout and stderr of start/end whitespace before returning.
		Can also log formatted stdout and stderr on failure.
		Otherwise, logs the output, unformatted and unstripped, as TRACE
		"""
		logger.debug("Calling '{}'".format(' '.join(cmd)))
		kwargs = copy(kwargs)
		if 'cwd' in kwargs and isinstance(kwargs['path'], PurePath):
			kwargs['cwd'] = str(kwargs['cwd'])
		try:
			x = subprocess.run(*[str(c) for c in cmd], capture_output=True, check=True, text=True, encoding='utf8', **kwargs)
			logger.trace("stdout: '{}'".format(x.stdout))
			logger.trace("stderr: '{}'".format(x.stdout))
			x.stdout = x.stdout.strip()
			x.stderr = x.stderr.strip()
			return x
		except subprocess.CalledProcessError as e:
			if log_fn is not None:
				IoTools.log_called_process_error(e, log_fn)
			raise

	@staticmethod
	def log_called_process_error(
			e: subprocess.CalledProcessError,
			log_fn: Callable[[str], None],
			wrap_length: int = 80
	) -> None:
		"""
		Outputs some formatted text describing the error with its full stdout and stderr.
		:param e: The error
		:param log_fn: For example, `logger.warning`
		:param wrap_length: The max number of characters of the header and footer around the stdout and stderr
				The output text is wrapped to this value - 4
				The full line can be longer than this because the text of the command is not wrapped
		"""
		wrap_length = max(10, wrap_length)
		log_fn("Failed on command:[\n{}\n]".format(indent("\n".join(['"' + x + '"' for x in e.cmd]), '\t')))
		log_fn("Received exit code {}".format(e.returncode))
		if e.stdout is not None and len(e.stdout.strip()) > 0:
			log_fn(' STDOUT '.center(wrap_length, '.'))
			log_fn(indent(wrap(e.stdout.strip(), wrap_length-4), '\t'))
			log_fn('.'*wrap_length)
		else:
			log_fn(Chars.dangled('no stdout '))
		if e.stderr is not None and len(e.stderr.strip()) > 0:
			log_fn(' STDERR '.center(wrap_length, '.'))
			log_fn(indent(wrap(e.stderr.strip(), wrap_length-4), '\t'))
			log_fn('.'*wrap_length)
		else:
			log_fn(Chars.dangled('no stderr '))


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
		self._raw = mode
		self.internal = self.__strip()
	def __repr__(self):
		return self.internal
	def __str__(self):
		return self.internal
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


COMPRESS_LEVEL = 9
ENCODING = 'utf8'


class FilesysTools(VeryCommonTools):

	@staticmethod
	def updir(n: int, *parts) -> Path:
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

	@staticmethod
	def try_cleanup(path: Path) -> None:
		"""
		Try to delete a file (probably temp file), if it exists, and log any PermissionError.
		"""
		path = Path(path)
		if path.exists():
			try:
				path.unlink()
			except PermissionError:
				logger.error("Permission error preventing deleting {}".format(path))

	@staticmethod
	def read_lines_file(path: PLike, ignore_comments: bool = False) -> Sequence[str]:
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

	@staticmethod
	def read_properties_file(path: PLike) -> Mapping[str, str]:
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

	@staticmethod
	def write_properties_file(properties: Mapping[Any, Any], path: Union[str, PurePath], mode: str = 'o'):
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

	@staticmethod
	def make_dirs(s: PLike) -> None:
		# '' can break on Windows
		if str(s) != '':
			Path(s).mkdir(exist_ok=True, parents=True)

	@staticmethod
	def save_json(data, path: PLike, mode: str = 'w') -> None:
		with FilesysTools.open_file(path, mode) as f:
			json.dump(data, f, ensure_ascii=False, cls=JsonEncoder)

	@staticmethod
	def load_json(path: PLike):
		with FilesysTools.open_file(path, 'r') as f:
			return json.load(f)

	@staticmethod
	def save_jsonpkl(data, path: PLike, mode: str = 'w') -> None:
		if jsonpickle is None:
			raise ImportError("No jsonpickle")
		FilesysTools.write_text(jsonpickle.encode(data), path, mode=mode)

	@staticmethod
	def load_jsonpkl(path: PLike) -> dict:
		if jsonpickle is None:
			raise ImportError("No jsonpickle")
		return jsonpickle.decode(FilesysTools.read_text(path))

	@staticmethod
	def read_bytes(path: PLike) -> bytes:
		with FilesysTools.open_file(path, 'rb') as f:
			return f.read()

	@staticmethod
	def read_text(path: PLike) -> str:
		with FilesysTools.open_file(path, 'r') as f:
			return f.read()

	@staticmethod
	def write_bytes(data: Any, path: PLike, mode: str = 'wb') -> None:
		if not OpenMode(mode).write or not OpenMode(mode).binary:
			raise BadCommandError("Cannot write bytes to {} in mode {}".format(path, mode))
		with FilesysTools.open_file(path, mode) as f:
			f.write(data)

	@staticmethod
	def write_text(data: Any, path: PLike, mode: str = 'w'):
		if not OpenMode(mode).write or OpenMode(mode).binary:
			raise BadCommandError("Cannot write text to {} in mode {}".format(path, mode))
		with FilesysTools.open_file(path, mode) as f:
			f.write(str(data))

	@staticmethod
	def prep_dir(path: PLike, exist_ok: bool) -> bool:
		"""
		Prepares a directory by making it if it doesn't exist.
		If exist_ok is False, calls logger.warning it already exists
		"""
		path = FilesysTools.sanitize_directory_path(path)
		exists = path.exists()
		# On some platforms we get generic exceptions like permissions errors, so these are better
		if exists and not path.is_dir():
			raise InvalidDirectoryException("Path {} exists but is not a file".format(path))
		if exists and not exist_ok:
			logger.warning("Directory {} already exists".format(path))
		if not exists:
			# NOTE! exist_ok in mkdir throws an error on Windows
			path.mkdir(parents=True)
		return exists

	@staticmethod
	def prep_file(path: PLike, overwrite: bool = True, append: bool = False) -> bool:
		"""Prepares a file path by making its parent directory (if it doesn't exist) and checking it."""
		# On some platforms we get generic exceptions like permissions errors, so these are better
		# TODO handle ignore
		path = FilesysTools.sanitize_file_path(path)
		exists = path.exists()
		if overwrite and append:
			raise BadCommandError("Can't append and overwrite file {}".format(path))
		if exists and not overwrite and not append:
			raise FileExistsError("Path {} already exists".format(path))
		elif exists and not path.is_file() and not path.is_symlink():  # TODO check link?
			raise InvalidFileException("Path {} exists but is not a file".format(path))
		# NOTE! exist_ok in mkdir throws an error on Windows
		if not path.parent.exists():
			Path(path.parent).mkdir(parents=True, exist_ok=True)
		return exists

	@staticmethod
	@contextmanager
	def open_file(path: PLike, mode: str):
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
			raise InvalidFileException("Path {} already exists".format(path))
		if not mode.read:
			FilesysTools.prep_file(path, overwrite=mode.overwrite, append=mode.append)
		if mode.gzipped:
			yield gzip.open(path, mode.internal, compresslevel=COMPRESS_LEVEL)
		elif mode.binary:
			yield open(path, mode.internal)
		else:
			yield open(path, mode.internal, encoding=ENCODING)

	@staticmethod
	def write_lines(iterable: Iterable[Any], path: PLike, mode: str = 'w') -> int:
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

	@staticmethod
	def sha1(x: SupportsBytes) -> str:
		return FilesysTools.hash_hex(x, hashlib.sha1)

	@staticmethod
	def sha256(x: SupportsBytes) -> str:
		return FilesysTools.hash_hex(x, hashlib.sha256)

	@staticmethod
	def hash_hex(x: SupportsBytes, algorithm: str) -> str:
		"""Return the hex-encoded hash of the object (converted to bytes)."""
		m = hashlib.new(algorithm)
		m.update(bytes(x))
		return m.hexdigest()

	@staticmethod
	def sanitize_file_path(path: PLike, show_warnings: bool = True) -> Path:
		return Path(FilesysTools.sanitize_filename(path, show_warnings))

	@staticmethod
	def sanitize_prepped_file_path(path: PLike, show_warnings: bool = True) -> Path:
		"""It's ok for the file to exist."""
		path = Path(FilesysTools.sanitize_file_path(path, show_warnings))
		FilesysTools.prep_file(path, True, False)
		return path

	@staticmethod
	def sanitize_directory_path(path: PLike, show_warnings: bool = True) -> Path:
		return Path(FilesysTools.sanitize_directory_name(path, show_warnings))

	@staticmethod
	def sanitize_prepped_directory_path(path: PLike, show_warnings: bool = True, exist_ok: bool = True) -> Path:
		path = Path(FilesysTools.sanitize_directory_name(path, show_warnings))
		FilesysTools.prep_dir(path, exist_ok=exist_ok)
		return path

	@staticmethod
	def sanitize_filename(path: PLike, show_warnings: bool = True) -> str:
		return FilesysTools._sanitize(path, True, show_warnings)

	@staticmethod
	def sanitize_directory_name(path: PLike, show_warnings: bool = True) -> str:
		if str(path) == '': path = '.'  # breaks on windows
		return FilesysTools._sanitize(path, False, show_warnings)

	@staticmethod
	def sanitize(*parts: str) -> Path:
		"""
		Preferred function. Sanitize from parts. Use instead of `Path(...)`.
		"""
		return Path(*[FilesysTools._sanitize(p, False, True) for p in parts])

	@staticmethod
	def _sanitize(path: PLike, is_file: bool, show_warnings: bool) -> str:
		path = str(path)
		if re.compile(r'[A-Z]:\\.*').fullmatch(path):
			# noinspection PyProtectedMember
			return str(Path(path[0:3]) / WindowsPaths._sanitize(path[3:], is_file=is_file, show_warnings=show_warnings))
		elif path == '.':
			return path  # it's ok, and this avoids a warning of '.' -> ''
		else:
			path = str(Path(path).expanduser())
			# noinspection PyProtectedMember
			return WindowsPaths._sanitize(path, is_file=is_file, show_warnings=show_warnings)


class ProgramTools:
	from klgists.misc.git import GitTools as __git_desc
	git_commit_hash = __git_desc.commit_hash
	git_describe = __git_desc.description


__all__ = ['ConsoleTools', 'IoTools', 'OpenMode', 'FilesysTools', 'ProgramTools']