from typing import Iterable

from colorama import Fore, Style

def warn_user(*lines: str):
	print()
	_print_to_user(['', *lines, ''], Fore.RED, top='_', bottom='_', sides='|')
	print()

def notify_user(*lines: str):
	print()
	_print_to_user(['', *lines, ''], Fore.BLUE, top='*', bottom='*', sides='*')
	print()

def notify_user_light(*lines: str):
	print()
	_print_to_user(['', *lines, ''], Style.BRIGHT, top='_', bottom='_', sides='')
	print()

def header_to_user(*lines: str):
	_print_to_user(lines, Style.BRIGHT, top='', bottom='_', sides='')

def _print_to_user(lines: Iterable[str], color: int, top: str, bottom: str, sides: str, line_length: int=100):
	def cl(text: str): print(str(color) + sides + text.center(line_length - 2*len(sides)) + sides)
	print(str(color) + top * line_length)
	for line in lines:
		cl(line)
	print(str(color) + bottom * line_length)

