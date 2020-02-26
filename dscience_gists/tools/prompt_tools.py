from typing import Iterable, Mapping, Callable, Optional
from enum import Enum
import logging
import os, shutil, stat
from pathlib import Path
import time
from colorama import Fore, Style
from dscience_gists.core import PathLike
from dscience_gists.tools.base_tools import BaseTools
from dscience_gists.core.exceptions import RefusingRequestError
from dscience_gists.tools.filesys_tools import FilesysTools

logger = logging.getLogger('dscience_gists')


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


class Deletion(Enum):
	NO = 1
	TRASH = 2
	HARD = 3


class DeletePrompter:
	CHOICES = [Deletion.NO.name.lower(), Deletion.TRASH.name.lower(), Deletion.HARD.name.lower()]

	def __init__(
			self,
			allow_dirs: bool = True,
			notify: bool = True,
			ignorable: bool = True,
			delete_fn: Callable[[PathLike], None] = FilesysTools.delete_surefire,
			trash_fn: Callable[[PathLike], None] = FilesysTools.trash,
			dry: bool = False
	):
		self.allow_dirs = allow_dirs
		self.notify, self.allow_ignore = notify, ignorable
		self.delete_fn, self.trash_fn = delete_fn, trash_fn
		self.dry = dry

	def prompt(self, path: PathLike):
		path = Path(path)
		if not self.allow_dirs and path.is_dir():
			raise RefusingRequestError("Cannot delete directory {}; only files are allowed.".format(path))
		elif not path.is_dir() and not path.is_file():
			raise RefusingRequestError("Cannot delete {}; only files and directories are allowed.".format(path))
		while True:
			print(Fore.BLUE + "Delete? [{}]".format('/'.join(DeletePrompter.CHOICES)), end='')
			cmdd = input('').strip()
			logger.debug("Received user input {}".format(cmdd))
			polled = self._poll(path, cmdd)
			if polled is not None: return polled

	def _poll(self, path: Path, command: str) -> Optional[Deletion]:
		# HARD DELETE
		if command.lower() == Deletion.HARD.name.lower():
			if not self.dry:
				self.delete_fn(path)
			if self.notify:
				print(Style.BRIGHT + "Permanently deleted {}".format(path))
			return Deletion.HARD
		# MOVE TO TRASH
		elif command.lower() == Deletion.TRASH.name.lower():
			if not self.dry:
				self.trash_fn(path)
			if self.notify:
				print(Style.BRIGHT + "Trashed {}.".format(path))
			return Deletion.TRASH
		# IGNORE
		elif command.lower() == Deletion.NO.name.lower() or len(command) == 0 and self.allow_ignore:
			return Deletion.NO
		# INVALID
		else:
			print(Fore.RED + "Enter {}".format(' or '.join(DeletePrompter.CHOICES)))
			return None


class PromptTools(BaseTools):

	@classmethod
	def prompt_yes_no(cls, msg: str) -> bool:
		while True:
			print(Fore.BLUE + msg + ' ', end='')
			command = input('')
			if command.lower() == 'yes':
				return True
			elif command.lower() == 'no':
				return False
			else:
				print(Fore.BLUE + "Enter 'yes' or 'no'.")

	@classmethod
	def slow_delete(cls, path: str, wait: int = 5, delete_fn: Callable[[str], None] = FilesysTools.delete_surefire):
		logger.debug("Deleting directory tree {} ...".format(path))
		print(Fore.BLUE + "Waiting for {}s before deleting {}: ".format(wait, path), end='')
		for i in range(0, wait):
			time.sleep(1)
			print(Fore.BLUE + str(wait - i) + ' ', end='')
		time.sleep(1)
		print(Fore.BLUE + '...', end='')
		delete_fn(path)
		print(Fore.BLUE + ' deleted.')
		logger.debug("Deleted directory tree {}".format(path))


__all__ = ['ColorMessages', 'PromptTools', 'DeletePrompter']
