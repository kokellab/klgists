from klgists.common.tools import *
from klgists.common.chars import *
from klgists.common.exceptions import ParsingError, BadCommandError, InvalidDirectoryException, InvalidFileException
from copy import copy
from textwrap import wrap, indent

import contextlib
import subprocess

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


class ProgramTools:
	from klgists.misc.git import GitTools as __git_desc
	git_commit_hash = __git_desc.commit_hash
	git_describe = __git_desc.description
