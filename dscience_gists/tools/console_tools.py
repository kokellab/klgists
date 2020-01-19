from typing import Union, Callable
import sys
from dscience_gists.tools import VeryCommonTools

class ConsoleTools(VeryCommonTools):

	CURSOR_UP_ONE = '\x1b[1A'
	ERASE_LINE = '\x1b[2K'

	@classmethod
	def confirm(cls, msg: Union[None, str, Callable[[], None]] = None) -> bool:
		"""
		Asks for a confirmation from the user using the bulliten input().
		:param msg: If None defaults to 'Confirm? [yes/no]'
		:return: True if the user answered 'yes'; False otherwise
		"""
		if msg is None: msg = "Confirm? [yes/no]"
		if isinstance(msg, str):
			msg = lambda: print(msg + ' ', end='')
		while True:
			msg()
			command = input('')
			if command.lower() == '/exit': break
			if command.lower() in ['yes', 'y']: return True
			elif command.lower() in ['no', 'n']: return False

	@classmethod
	def clear_line(cls, n: int = 1) -> None:
		"""
		Writes control characters to stdout to delete the previous line and move the curser up.
		This only works in a shell.
		:param n: The number of lines to erase
		"""
		for _ in range(n):
			sys.stdout.write(ConsoleTools.CURSOR_UP_ONE)
			sys.stdout.write(ConsoleTools.ERASE_LINE)


__all__ = ['ConsoleTools']
