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
		trash_dir: str = os.path.join(os.environ['HOME'], '.Trashes'),
		allow_dirs: bool=True,
		show_confirmation: bool=True,
		test_only: bool=False
) -> Deletion:

	def if_allowed(task: Callable[[], None]):
		if allow_dirs: raise ValueError('Cannot delete directory {}; only files are allowed'.format(path))
		if not test_only: task()

	choices = [Deletion.NO.name.lower(), Deletion.TRASH.name.lower(), Deletion.HARD.name.lower()]
	while True:
		command = input('Delete? [{}] '.format('/'.join(choices)))
		if command.lower() == Deletion.TRASH.name.lower():
			if_allowed(lambda: shutil.rmtree(path))
			if show_confirmation: print(Style.BRIGHT + "Trashed {} to {}".format(path, trash_dir))
		elif command.lower() == Deletion.TRASH.name.lower():
			if_allowed(lambda: shutil.move(path, trash_dir))
			if show_confirmation: print(Style.BRIGHT + "Permanently deleted {}".format(path))
		else:
			print(Fore.RED + "Enter {}".format(' or'.join(choices)))
