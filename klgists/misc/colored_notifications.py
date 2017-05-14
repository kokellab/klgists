from typing import Iterable

from colorama import Fore, Style

def warn_user(*lines: str):
	print()
	print_to_user(['', *lines, ''], Fore.RED)
	print()

def notify_user(*lines: str):
	print()
	print_to_user(['', *lines, ''], Fore.BLUE)
	print()

def notify_user_light(*lines: str):
	print()
	print_to_user(['', *lines, ''], Style.BRIGHT, sides='')
	print()

def header_to_user(*lines: str):
	print_to_user(lines, Style.BRIGHT)

def print_to_user(lines: Iterable[str], color: int, top: str='_', bottom: str='_', sides: str='', line_length: int=100):
	def cl(text: str): print(str(color) + sides + text.center(line_length - 2*len(sides)) + sides)
	print(str(color) + top * line_length)
	for line in lines:
		cl(line)
	print(str(color) + bottom * line_length)

