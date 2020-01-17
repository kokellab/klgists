from __future__ import annotations
import os, json, sys, io
import unicodedata
from itertools import chain
import signal
import operator
import logging
from contextlib import contextmanager, redirect_stdout
from datetime import date, datetime
from typing import Iterator, TypeVar, Iterable, Optional, List, Any, Sequence, Mapping, overload, Union, Callable
from hurry.filesize import size as hsize
from klgists.common.exceptions import LookupFailedException, MultipleMatchesException, ParsingFailedException, LengthMismatchError

logger = logging.getLogger('klgists')

def look(obj: object, attrs: str) -> any:
	if not isinstance(attrs, str) and isinstance(attrs, Iterable): attrs = '.'.join(attrs)
	try:
		return operator.attrgetter(attrs)(obj)
	except AttributeError: return None

def flatmap(func, *iterable):
	return chain.from_iterable(map(func, *iterable))

def flatten(*iterable):
	return list(chain.from_iterable(iterable))

class DevNull:
	def write(self, msg): pass

T = TypeVar('T', covariant=True)

class frozenlist(Sequence):
	"""
	An immutable sequence backed by a list.
	The sole advantage over a tuple is the list-like __str__ with square brackets, which may be less confusing to a user.
	"""
	def __init__(self, *items: Iterable[T]):
		self.__items = list(items)

	@overload
	def __getitem__(self, i: int) -> T:
		return self.__items[i]

	@overload
	def __getitem__(self, s: slice) -> frozenlist[T]:
		return frozenlist(self.__items[s])

	def __getitem__(self, item) -> T:
		if isinstance(item, slice):
			return self[item]
		else:
			return self[item]

	def __len__(self) -> int:
		return len(self.__items)

	def __repr__(self):
		return repr(self.__items)

	def __str__(self):
		return repr(self.__items)


pjoin = os.path.join
pexists = os.path.exists
plexists = os.path.lexists
pfile = os.path.isfile
pdir = os.path.isfile
pdirname = os.path.dirname
pfsize = os.path.getsize

def pardir(path: str, depth: int=1):
	for _ in range(-1, depth):
		path = os.path.dirname(path)
	return path

def grandpardir(path: str):
	return pardir(path, 2)

def get_log_function(log: Union[None, str, Callable[[str], None]]) -> Callable[[str], None]:
	"""
	Gets a logging function from user input.
	The rules are:
		- If None, uses logger.info
		- If 'print' or 'stdout',  use sys.stdout.write
		- If 'stderr', use sys.stderr.write
		- If another str or int, try using that logger level (raises an error if invalid)
		- If callable, returns it
		- If it has a callable method called 'write', uses that
	:return: A function of the log message that returns None
	"""
	if log is None:
		return logger.info
	elif log in ['print', 'stdout']:
		return lambda msg: sys.stdout.write(msg)
	elif log == 'stderr':
		return lambda msg: sys.stderr.write(msg)
	elif isinstance(log, int):
		return getattr(logger, logging.getLevelName(log))
	elif isinstance(log, str):
		return getattr(logger, logging.getLevelName(log.upper()))
	elif callable(log):
		return log
	elif hasattr(log, 'write') and getattr(log, 'write'):
		return getattr(log, 'write')
	else:
		raise TypeError("Log type {} not known".format(type(log)))

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
	def split(self, x): return self.__cio.getvalue().split(x)

@contextmanager
def tee(log: str):
	"""Redirects stdout and stderr to a log file but still prints to the original streams."""
	if isinstance(log, str): log = open(log, 'a')
	try:
		sys.stdout = DelegatingWriter(sys.__stdout__, log)
		sys.stderr = DelegatingWriter(sys.__stderr__, log)
		yield
	finally:
		sys.stdout = sys.__stdout__
		sys.stderr = sys.__stderr__
		log.close()

@contextmanager
def capture():
	"""
	Suppress output to stdout, instead capturing it to a variable.
	>>> with Tools.capture() as cap:
	... 	if 'finished' in cap.value:
	... 		print('; '.join(cap.lines))
	:return: A Capture instance, which implements a lazy string
	"""
	with redirect_stdout(io.StringIO()) as v:
		yield Capture(v)

def forever() -> Iterator[int]:
	"""
	Yields i for i in range(0, infinity).
	Useful for simplifying a i = 0; while True: i += 1 block.
	"""
	i = 0
	while True:
		yield i
		i += 1

def parse_bool(s: str) -> bool:
	"""
	Parses a 'true'/'false' string to a bool, ignoring case.
	:raises: KaleValueError If neither true nor false
	"""
	if s.lower() == 'false':
		return False
	if s.lower() == 'true':
		return True
	raise ValueError("{} is not true/false".format(s))

def strip_off_start(s: str, pre: str) -> str:
	"""
	Strips the full string `pre` from the start of `str`.
	See `Tools.strip_off` for more info.
	"""
	assert isinstance(pre, str), "{} is not a string".format(pre)
	if s.startswith(pre):
		s = s[len(pre):]
	return s

def strip_off_end(s: str, suf: str) -> str:
	"""
	Strips the full string `suf` from the end of `str`.
	See `Tools.strip_off` for more info.
	"""
	assert isinstance(suf, str), "{} is not a string".format(suf)
	if s.endswith(suf):
		s = s[:-len(suf)]
	return s

T = TypeVar('T')
def try_index_of(element: List[T], list_element: T) -> Optional[T]:
	try:
		index_element = list_element.index(element)
		return index_element
	except ValueError:
		return None

def decorator(cls):
	return cls


def zip_strict(*args):
	"""Same as zip(), but raises an IndexError if the lengths don't match."""
	# we need to catch these cases before or they'll fail
	# in particular, 1 element would fail with a LengthMismatchError
	# and 0 elements would loop forever
	if len(args) < 2:
		return zip(*args)
	iters = [iter(axis) for axis in args]
	n_elements = 0
	failures = []
	while len(failures) == 0:
		values = []
		failures = []
		for axis, iterator in enumerate(iters):
			try:
				values.append(next(iterator))
			except StopIteration:
				failures.append(axis)
		if len(failures) == 0:
			yield tuple(values)
		elif len(failures) == 1:
			raise LengthMismatchError("Too few elements ({}) along axis {}".format(n_elements, failures[0]))
		elif len(failures) < len(iters):
			raise LengthMismatchError("Too few elements ({}) along axes {}".format(n_elements, failures))
		n_elements += 1

def zip_list(*args) -> List[Any]:
	"""Same as zip_strict, but converts to a list and can provide a more detailed error message."""
	try:
		return list(zip_strict(*args))
	except LengthMismatchError:
		raise LengthMismatchError("Length mismatch in zip_strict: Sizes are {}".format([len(x) for x in args])) from None
zip_strict_list = zip_list  # for historical use

def only(sequence: Iterable[Any]) -> Any:
	"""
	Returns either the SINGLE (ONLY) UNIQUE ITEM in the sequence or raises an exception.
	Each item must have __hash__ defined on it.
	:param sequence: A list of any items (untyped)
	:return: The first item the sequence.
	:raises: ValarLookupError If the sequence is empty
	:raises: MultipleMatchesException If there is more than one unique item.
	"""
	st = set(sequence)
	if len(st) > 1:
		raise MultipleMatchesException("More then 1 item in {}".format(sequence))
	if len(st) == 0:
		raise LookupFailedException("Empty sequence")
	return next(iter(st))


def read_lines_file(path: str, ignore_comments: bool = False) -> Sequence[str]:
	"""
	Returns a list of lines in a file, potentially ignoring comments.
	:param path: Read the file at this local path
	:param ignore_comments: Ignore lines beginning with #, excluding whitespace
	:return: The lines, with surrounding whitespace stripped
	"""
	lines = []
	with open(path) as f:
		for line in f.readlines():
			line = line.strip()
			if not ignore_comments or not line.startswith('#') and not len(line.strip()) == 0:
				lines.append(line)
	return lines

def write_properties_file(path: str, properties: Mapping[str, Any], overwrite: bool = False) -> None:
	if not overwrite and os.path.exists(path):
		raise FileExistsError("The properties file {} already exists".format(path))
	with open(path, 'w') as f:
		for key, value in properties.items():
			f.write(str(key) + '=' + escape_for_properties(value) + '\n')

def read_properties_file(path: str) -> Mapping[str, str]:
	"""
	Reads a .properties file, which is a list of lines with key=value pairs (with an equals sign).
	Lines beginning with # are ignored.
	Each line must contain exactly 1 equals sign.
	:param path: Read the file at this local path
	:return: A dict mapping keys to values, both with surrounding whitespace stripped
	"""
	dct = {}
	with open(path) as f:
		for i, line in enumerate(f.readlines()):
			line = line.strip()
			if len(line) == 0 or line.startswith('#'): continue
			if line.count('=') != 1:
				raise ParsingFailedException("Bad line {} in {}".format(i, path))
			parts = line.split('=')
			dct[parts[0].strip()] = parts[1].strip()
	return dct

def json_serial(obj):
	"""JSON serializer for objects not serializable by default json code.
	From jgbarah at https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable
	"""
	if isinstance(obj, (datetime, date)):
		return obj.isoformat()
	try:
		import peewee
		if isinstance(obj, peewee.Field):
			return type(obj).__name__
	except ImportError: pass
	raise TypeError("Type %s not serializable" % type(obj))

def pretty_dict(dct: dict) -> str:
	"""Returns a pretty-printed dict, complete with indentation. Will fail on non-JSON-serializable datatypes."""
	return json.dumps(dct, default=json_serial, sort_keys=True, indent=4)

def pp_dict(dct: dict) -> None:
	"""Pretty-prints a dict to stdout."""
	print(pretty_dict(dct))

def pp_size(obj: object) -> None:
	"""Prints to stdout a human-readable string of the memory usage of arbitrary Python objects. Ex: 8M for 8 megabytes."""
	print(hsize(sys.getsizeof(obj)))

def sanitize_str(value: str) -> str:
	"""Removes Unicode control (Cc) characters EXCEPT for tabs (\t), newlines (\n only), line separators (U+2028) and paragraph separators (U+2029)."""
	return "".join(ch for ch in value if unicodedata.category(ch) != 'Cc' and ch not in {'\t', '\n', '\u2028', '\u2029'})

def escape_for_properties(value: Any) -> str:
	return sanitize_str(str(value).replace('\n', '\u2028'))

def escape_for_tsv(value: Any) -> str:
	return sanitize_str(str(value).replace('\n', '\u2028').replace('\t', ' '))


class Timeout:
	def __init__(self, seconds: int = 10, error_message='Timeout'):
		self.seconds = seconds
		self.error_message = error_message
	def handle_timeout(self, signum, frame):
		raise TimeoutError(self.error_message)
	def __enter__(self):
		signal.signal(signal.SIGALRM, self.handle_timeout)
		signal.alarm(self.seconds)
	def __exit__(self, type, value, traceback):
		signal.alarm(0)

