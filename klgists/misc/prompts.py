import shutil
import os
import time
import stat
from enum import Enum
from typing import Callable, Optional
from colorama import Fore, Style

from klgists.common.exceptions import RefusingRequestException
from klgists import logger


class Deletion(Enum):
	NO = 1
	TRASH = 2
	HARD = 3


def prompt_yes_no(msg: str) -> bool:
	while True:
		print(Fore.BLUE + msg + ' ', end='')
		command = input('')
		if command.lower() == 'yes':
			return True
		elif command.lower() == 'no':
			return False
		else:
			print(Fore.BLUE + "Enter 'yes' or 'no'.")

			
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
		shutil.rmtree(path, ignore_errors=True) # ignore_errors because of Windows
		try:
			os.remove(path)  # again, because of Windows
		except IOError: pass  # almost definitely because it doesn't exist
	else:
		os.remove(path)
	logger.debug("Permanently deleted {}".format(path))
	return chmod_err

	
def slow_delete(path: str, wait: int = 5, delete_fn: Callable[[str], None] = deletion_fn):
	logger.debug("Deleting directory tree {} ...".format(path))
	print(Fore.BLUE + "Waiting for {}s before deleting {}: ".format(wait, path), end='')
	for i in range(0, wait):
		time.sleep(1)
		print(Fore.BLUE + str(wait-i) + ' ', end='')
	time.sleep(1)
	print(Fore.BLUE + '...', end='')
	chmod_err = delete_fn(path)
	print(Fore.BLUE + ' deleted.')
	if chmod_err is not None:
		try:
			raise chmod_err
		except:
			logger.warning("Couldn't chmod {}".format(path), exc_info=True)
	logger.debug("Deleted directory tree {}".format(path))


def prompt_and_delete(
		path: str,
		trash_dir: str = os.path.join(os.environ['HOME'], '.Trash'),
		allow_dirs: bool=True,
		show_confirmation: bool=True,
		dry: bool=False,
		allow_ignore: bool=True,
		delete_fn: Callable[[str], None] = deletion_fn
) -> Deletion:
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
		raise RefusingRequestException('Cannot delete directory {}; only files are allowed'.format(path))

	choices = [Deletion.NO.name.lower(), Deletion.TRASH.name.lower(), Deletion.HARD.name.lower()]

	def poll(command: str) -> Deletion:

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
		command = input('').strip()
		#logger.debug("Received user input {}".format(command))
		polled = poll(command)
		if polled is not None: return polled


__all__ = ['prompt_yes_no', 'slow_delete', 'prompt_and_delete', 'deletion_fn']
