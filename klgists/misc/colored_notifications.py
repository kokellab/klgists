from typing import Iterable, Mapping, Callable, Optional
from enum import Enum
from colorama import Fore, Style


class NotificationLevel(Enum):
	INFO = 1
	SUCCESS = 2
	NOTICE = 3
	WARNING = 4
	FAILURE = 5


class ColorMessages:

	DEFAULT_COLOR_MAP = {
		NotificationLevel.INFO: Style.BRIGHT,
		NotificationLevel.NOTICE: Fore.BLUE,
		NotificationLevel.SUCCESS: Fore.GREEN,
		NotificationLevel.WARNING: Fore.MAGENTA,
		NotificationLevel.FAILURE: Fore.RED
	}

	def __init__(self, color_map: Optional[Mapping[NotificationLevel, int]] = None, log_fn: Optional[Callable[[str], None]] = None, **kwargs):
		"""
		Constructs a new environment for colored console messages.
		:param color_map: A map from level to colors in colorama to override ColorMessages.DEFAULT_COLOR_MAP
		:param log_fn: If set, additionally logs every message with this function
		:param kwargs: Arguments 'top', 'bottom', 'sides', and 'line_length'
		"""
		_cmap = ColorMessages.DEFAULT_COLOR_MAP
		_cmap.update(color_map)
		assert set(_cmap.keys()) == set(NotificationLevel.__members__.keys()),\
			"Color map {} must match levels {}".format(_cmap, NotificationLevel.__members__)
		self._color_map, self._log_fn, self._kwargs = _cmap, log_fn, kwargs

	def thin(self, level: NotificationLevel, *lines: str):
		self._print(lines, self._color_map[level], **self._kwargs)

	def thick(self, level: NotificationLevel, *lines: str):
		self._print(['\n', lines, '\n'], self._color_map[level], **self._kwargs)

	def _print(self, lines: Iterable[str], color: int, top: str = '_', bottom: str = '_', sides: str = '', line_length: int = 100):
		def cl(text: str): print(str(color) + sides + text.center(line_length - 2 * len(sides)) + sides)
		print(str(color) + top * line_length)
		self._log(top * line_length)
		for line in lines:
			self._log(line)
			cl(line)
		print(str(color) + bottom * line_length)
		self._log(bottom * line_length)

	def _log(self, message):
		if self._log_fn:
			self._log_fn(message)


__all__ = ['ColorMessages']
