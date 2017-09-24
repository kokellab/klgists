import shutil
import os
from enum import Enum
from colorama import Fore, Style


class Deletion(Enum):
	NO = 1
	TRASH = 2
	HARD = 3

def prompt_yes_no(msg: str) -> bool:
	while True:
		command = input(msg + ' ')
		if command.lower() == 'yes':
			return True
		elif command.lower() == 'no':
			return False
		else:
			print(Fore.RED + "Enter 'yes' or 'no'.")


def prompt_and_delete(
		path: str,
		trash_dir: str = os.path.join(os.environ['HOME'], '.Trash'),
		allow_dirs: bool=True,
		show_confirmation: bool=True,
		dry: bool=False,
		allow_ignore: bool=True
) -> Deletion:
	"""

	:param path:
	:param trash_dir: The directory of a trashbin ('~/.Trash' by default)
	:param allow_dirs: Allow deleting full directory trees; set to False for safety
	:param show_confirmation: Print the action to stdout (ex: 'Trashed abc.txt to ~/.Trash')
	:param dry: If True, will only return the Deletion object to be handled outside
	:param allow_ignore: Allow entering an empty string to mean ignore
	:return: A Deletion enum reflecting the chosen action
	"""

	assert allow_dirs or not os.path.isdir(path), 'Cannot delete directory {}; only files are allowed'.format(path)

	choices = [Deletion.NO.name.lower(), Deletion.TRASH.name.lower(), Deletion.HARD.name.lower()]

	def poll(command: str) -> Deletion:

		if command.lower() == Deletion.HARD.name.lower():
			if show_confirmation: print(Style.BRIGHT + "Permanently deleted {}".format(path))
			if not dry:
				if os.path.isdir(path): shutil.rmtree(path)
				else: os.remove(path)
			return Deletion.HARD

		elif command.lower() == Deletion.TRASH.name.lower():
			if not dry:
				shutil.move(path, trash_dir)
			if show_confirmation: print(Style.BRIGHT + "Trashed {} to {}".format(path, trash_dir))
			return Deletion.TRASH

		elif command.lower() == Deletion.NO.name.lower() or len(command) == 0 and allow_ignore:
			return Deletion.NO

		else:
			print(Fore.RED + "Enter {}".format(' or '.join(choices)))
			return None

	while True:
		command = input('Delete? [{}] '.format('/'.join(choices))).strip()
		polled = poll(command)
		if polled is not None: return polled
