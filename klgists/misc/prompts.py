import shutil
import os
from enum import Enum
from typing import Callable
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
		test_only: bool=False,
		allow_ignore: bool=True
) -> Deletion:

	assert allow_dirs or not os.path.isdir(path), 'Cannot delete directory {}; only files are allowed'.format(path)

	choices = [Deletion.NO.name.lower(), Deletion.TRASH.name.lower(), Deletion.HARD.name.lower()]

	def poll(command: str) -> Deletion:

		if command.lower() == Deletion.HARD.name.lower():
			if show_confirmation: print(Style.BRIGHT + "Permanently deleted {}".format(path))
			if os.path.isdir(path): shutil.rmtree(path)
			else: os.remove(path)
			return Deletion.HARD

		elif command.lower() == Deletion.TRASH.name.lower():
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
