import os, logging, datetime
from typing import Optional

from klgists.common.exceptions import PathIsNotDirectoryException

class FlexibleLogger:
	"""
	Usage:
	FlexibleLogger().add_stdout().add_file('abc.log')
	"""

	_underlying = None
	_formatter = None # type: logging.Formatter
	datetime_started = None  # type: datetime.datetime

	def __init__(self, name: Optional[str] = None, formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')):
		"""Initializes a logger that can write to a log file and/or stdout."""
		self._underlying = logging.getLogger(name)
		self._underlying.setLevel(logging.NOTSET)
		self._formatter = formatter
		self.datetime_started = datetime.datetime.now()

	def add_file(self, path: str, level: int = logging.DEBUG):
		self._make_dirs(os.pardir(path))
		return self._add(logging.FileHandler(path), level)

	def add_stdout(self, level: int = logging.INFO):
		return self._add(logging.StreamHandler(), level)

	def add_handler(self, handler: logging.Handler):
		self._underlying.addHandler(handler)
		return self

	def _add(self, handler, level):
		handler.setLevel(level)
		handler.setFormatter(self._formatter)
		self._underlying.addHandler(handler)
		return self

	def _make_dirs(self, output_dir: str) -> None:
		# note that we can't import from klgists.files (common shouldn't depend on files)
		if not os.path.exists(output_dir):
			os.makedirs(output_dir)
		elif not os.path.isdir(output_dir):
			raise PathIsNotDirectoryException("{} already exists and is not a directory".format(output_dir))



class LoggingFormatterBuilder:
	"""
	Builder for those of us who hate the Python logging Formatter syntax and can't remember the options.
	Example usage:
	formatter = LoggingFormatterBuilder()\
		.level_name_fixed_width()\
		.asc_time()\
		.thread_name(left=' [', right=':')\
		.line_num(left='', right=']')\
		.message(left=': ')\
		.build()
	"""
	_s = None
	def __init__(self) -> None: self._s = ''
	def __repr__(self) -> str: return "LoggingFormatterBuilder({})".format(self._s)
	def __str__(self) -> str: return repr(self)

	def level_num(self, left: str = ' ', right: str = ''): self._s += left + '%(levelno)s' + right; return self
	def level_name(self, left: str = ' ', right: str = ''): self._s += left + '%(levelname)s' + right; return self
	def level_name_fixed_width(self, left: str = ' ', right: str = ''): self._s += left + '%(levelname)-8s' + right; return self
	def name(self, left: str = ' ', right: str = ''): self._s += left + '%(name)s' + right; return self
	def module(self, left: str = ' ', right: str = ''): self._s += left + '%(module)s' + right; return self
	def message(self, left: str = ' ', right: str = ''): self._s += left + '%(message)s' + right; return self
	def thread_id(self, left: str = ' ', right: str = ''): self._s += left + '%(thread)d' + right; return self
	def thread_name(self, left: str = ' ', right: str = ''): self._s += left + '%(threadName)s' + right; return self
	def asc_time(self, left: str = ' ', right: str = ''): self._s += left + '%(asctime)s' + right; return self
	def line_num(self, left: str = ' ', right: str = ''): self._s += left + '%(lineno)d' + right; return self
	def other(self, format: str, left: str = ' ', right: str = ''): self._s += left + format + right; return self

	def build(self) -> logging.Formatter:
		return logging.Formatter(self._s[min(1, len(self._s)) :])


__all__ = ['FlexibleLogger', 'LoggingFormatterBuilder']

