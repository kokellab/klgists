from __future__ import annotations
import logging, enum
from functools import total_ordering
from contextlib import contextmanager
from typing import Union, Mapping, Generator


@enum.unique
@total_ordering
class _LogLevel(enum.Enum):
	NOTSET = logging.NOTSET
	TRACE = 5
	DEBUG = logging.DEBUG
	MINOR = 15
	INFO = logging.INFO
	CAUTION = 25
	WARNING = logging.WARNING
	NOTICE = 35
	ERROR = logging.ERROR
	CRITICAL = logging.CRITICAL

	@classmethod
	def of(cls, value: Union[int, str]) -> _LogLevel:
		if isinstance(value, str):
			value = value.upper()
			if value == 'WARN': return _LogLevel.WARNING
			if value == 'FATAL': return _LogLevel.CRITICAL
			for v in _LogLevel:
				if v.name == value:
					return v
		elif isinstance(value, int):
			for v in _LogLevel:
				if v.value == value:
					return v
		raise KeyError("No log level {}".format(value))

	def __lt__(self, other):
		if not isinstance(other, _LogLevel):
			raise TypeError("{} is not a log level".format(other))
		return self.value < other.value

# TODO duplicated
class LogLevel:

	NOTSET = logging.NOTSET
	TRACE = 5
	DEBUG = logging.DEBUG
	MINOR = 15
	INFO = logging.INFO
	CAUTION = 25
	WARNING = logging.WARNING
	NOTICE = 35
	ERROR = logging.ERROR
	CRITICAL = logging.CRITICAL

	@classmethod
	def levels(cls) -> Mapping[str, int]:
		return {e.name: e.value for e in _LogLevel}

	@classmethod
	def standard(cls) -> Mapping[str, int]:
		return {e.name: e.value for e in [_LogLevel.DEBUG, _LogLevel.INFO, _LogLevel.WARNING, _LogLevel.ERROR, _LogLevel.CRITICAL]}

	@classmethod
	def nonstandard(cls) -> Mapping[str, int]:
		return {e.name: e.value for e in [_LogLevel.TRACE, _LogLevel.MINOR, _LogLevel.CAUTION, _LogLevel.NOTICE]}

	@classmethod
	def initalize(cls):
		for name, value in LogLevel.nonstandard().items():
			setattr(logging, name, value)
			logging.addLevelName(value, name)

	@classmethod
	def get_int(cls, level: Union[int, str]) -> int:
		if isinstance(level, _LogLevel): return level.value
		return _LogLevel.of(level).value

	@classmethod
	def get_name(cls, level: Union[int, str]) -> str:
		if isinstance(level, _LogLevel): return level.name
		return _LogLevel.of(level).value.name


class AdvancedLogger(logging.Logger):
	"""
	Has a workaround for a Jupyter notebook bug.
	Can be suppressed using `with logger.suppressed():`.
	Weirdly, this works, while changing the minimum log level doesn't.
	Also adds new levels:
		- CAUTION: A less-concerning warning
		- NOTICE: Slightly higher than warning but doesn't indicate a potential problem
		- MINOR:  Information that is less important than INFO but isn't just for debugging
		- TRACE:  Low-level debug info

	To create:
	```
	LogLevel.initalize()
	logger = KaleLogger.create('myproject')
	log_factory = KaleRecordFactory(7, 13, 5).modifying(logger)
	logger.setLevel('INFO')   # good start; can be changed
	```
	"""
	@contextmanager
	def suppressed(self, suppress: bool = True, universe: bool = False) -> Generator[None, None, None]:
		"""
		Temporarily suppresses logging from kale, and globally if `universe=True`.
		Yields as a context manager.
		:param suppress: If False, ignores (useful to avoid if-else)
		:param universe: Disable all logging strictly below critical. Calls `logging.disable`
		"""
		if suppress: self._suppressed = True
		if suppress and universe: logging.disable(logging.ERROR)
		try:
			yield self
		finally:
			if suppress:
				# noinspection PyAttributeOutsideInit
				self._suppressed = False
				if universe:
					logging.disable(logging.NOTSET)

	@contextmanager
	def suppressed_other(self, name: str, suppress: bool = True, below: Union[int, str] = logging.ERROR) -> Generator[None, None, None]:
		"""
		Temporarily suppress logging for another logger name.
		Yields as a context manager.
		:param name: The name of the other logger, such as 'pandas'
		:param suppress: If False, ignores (useful to avoid if-else)
		:param below: Suppress only logging with levels strictly lower than this
		"""
		below = LogLevel.get_int(below)
		ell = logging.getLogger(name)
		prior = ell.getEffectiveLevel()
		if suppress:
			ell.setLevel(below)
		try:
			yield self
		finally:
			ell.setLevel(prior)

	@contextmanager
	def with_level(self, level: Union[int, str]) -> Generator[None, None, None]:
		original = self.getEffectiveLevel()
		try:
			self.setLevel(level)
			yield self
		finally:
			self.setLevel(original)

	@contextmanager
	def with_max_level(self, level: Union[int, str]) -> Generator[None, None, None]:
		original = self.getEffectiveLevel()
		level = LogLevel.get_int(level)
		try:
			self.setLevel(max(level, original))
			yield self
		finally:
			self.setLevel(original)

	def notice(self, msg, *args, **kwargs) -> None:
		"""
		Not a problem, just a more importance notice than INFO.
		Use for important events or major information.
		Slightly higher level than WARNING.
		"""
		if self.isEnabledFor(LogLevel.NOTICE):
			self._log(LogLevel.NOTICE, msg, args, **kwargs)

	def caution(self, msg, *args, **kwargs) -> None:
		"""
		A less concerning warning.
		Use for cases that are probably not issues.
		Slightly higher level than INFO.
		"""
		if self.isEnabledFor(LogLevel.CAUTION):
			self._log(LogLevel.CAUTION, msg, args, **kwargs)

	def minor(self, msg, *args, **kwargs) -> None:
		"""
		Lower-level information, but not for debugging.
		The level is between debug and info.
		"""
		if self.isEnabledFor(LogLevel.MINOR):
			self._log(LogLevel.MINOR, msg, args, **kwargs)

	def trace(self, msg, *args, **kwargs) -> None:
		"""
		Information that would only be used for debugging.
		Lower level than debug.
		"""
		if self.isEnabledFor(LogLevel.TRACE):
			self._log(LogLevel.TRACE, msg, args, **kwargs)

	def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False) -> None:
		if not self._suppressed and level < logging.CRITICAL:
			super()._log(level, msg, args, exc_info, extra, stack_info)

	@classmethod
	def create(cls, name: str):
		# noinspection PyTypeChecker
		ell: AdvancedLogger = logging.getLogger(name)
		ell.__class__ = AdvancedLogger
		ell._suppressed = False
		return ell

	@classmethod
	@property
	def levels(cls) -> Mapping[str, int]:
		return LogLevel.levels()


__all__ = ['AdvancedLogger', 'LogLevel']
