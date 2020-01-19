from typing import Iterable, Mapping, Callable, Optional
from enum import Enum
import logging
import os, shutil, stat
import time
from colorama import Fore, Style
from dscience_gists.core.exceptions import RefusingRequestError
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


def deletion_fn(path) -> Optional[Exception]:
	"""
	Deletes files or directories, which should work even in Windows.
	:return Returns None, or an Exception for minor warnings
	"""
	# we need this because of Windows
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

class Deletion(Enum):
	NO = 1
	TRASH = 2
	HARD = 3


class PromptTools:

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
	def slow_delete(cls, path: str, wait: int = 5, delete_fn: Callable[[str], None] = deletion_fn):
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

	@classmethod
	def prompt_and_delete(
			cls,
			path: str,
			trash_dir: str = os.path.join(os.environ['HOME'], '.Trash'),
			allow_dirs: bool = True,
			show_confirmation: bool = True,
			dry: bool = False,
			allow_ignore: bool = True,
			delete_fn: Callable[[str], None] = deletion_fn
	) -> Optional[Deletion]:
		"""

		:param path:
		:param trash_dir: The directory of a trashbin ('~/.Trash' by default)
		:param allow_dirs: Allow deleting full directory trees; set to False for safety
		:param show_confirmation: Print the action to stdout (ex: 'Trashed abc.txt to ~/.Trash')
		:param dry: If True, will only return the Deletion object to be handled outside
		:param allow_ignore: Allow entering an empty string to mean ignore
		:return: A Deletion enum reflecting the chosen action
		:param delete_fn: Function that actually deletes
		"""

		if not allow_dirs and os.path.isdir(path):
			raise RefusingRequestError('Cannot delete directory {}; only files are allowed'.format(path))
		choices = [Deletion.NO.name.lower(), Deletion.TRASH.name.lower(), Deletion.HARD.name.lower()]
		def poll(command: str) -> Optional[Deletion]:
			if command.lower() == Deletion.HARD.name.lower():
				if show_confirmation: print(Style.BRIGHT + "Permanently deleted {}".format(path))
				if dry:
					logger.debug("Operating in dry mode. Would otherwise have deleted {}".format(path))
				else:
					delete_fn(path)
					logger.debug("Permanently deleted {}".format(path))
				return Deletion.HARD

			elif command.lower() == Deletion.TRASH.name.lower():
				if dry:
					logger.debug("Operating in dry mode. Would otherwise have trashed {} to {}".format(path, trash_dir))
				else:
					shutil.move(path, trash_dir)
					logger.debug("Trashed {} to {}".format(path, trash_dir))
				if show_confirmation: print(Style.BRIGHT + "Trashed {} to {}".format(path, trash_dir))
				return Deletion.TRASH

			elif command.lower() == Deletion.NO.name.lower() or len(command) == 0 and allow_ignore:
				logger.debug("Will not delete {}".format(path))
				return Deletion.NO
			else:
				print(Fore.RED + "Enter {}".format(' or '.join(choices)))
				return None
		while True:
			print(Fore.BLUE + "Delete? [{}]".format('/'.join(choices)), end='')
			cmdd = input('').strip()
			logger.debug("Received user input {}".format(cmdd))
			polled = poll(cmdd)
			if polled is not None: return polled


__all__ = ['ColorMessages', 'PromptTools']
