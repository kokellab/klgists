from typing import Iterable

from colorama import Fore, Style

def warn_user(*lines: str):
	print()
	warn_thin(*lines)
	print()
def warn_thin(*lines: str):
	print_to_user(['', *lines, ''], Fore.RED)

def notify_user(*lines: str):
	print()
	notify_thin(*lines)
	print()
def notify_thin(*lines: str):
	print_to_user(['', *lines, ''], Fore.BLUE)

def success_to_user(*lines: str):
	print()
	success_to_user_thin(*lines)
	print()
def success_to_user_thin(*lines: str):
	print_to_user(['', *lines, ''], Fore.GREEN)

def concern_to_user(*lines: str):
	print()
	concern_to_user_thin(*lines)
	print()
def concern_to_user_thin(*lines: str):
	print_to_user(['', *lines, ''], Fore.YELLOW)

def notify_user_light(*lines: str):
	print()
	notify_light_thin(*lines)
	print()
def notify_light_thin(*lines: str):
	print_to_user(['', *lines, ''], Style.BRIGHT, sides='')

def header_to_user(*lines: str):
	print_to_user(lines, Style.BRIGHT)

def print_to_user(lines: Iterable[str], color: int, top: str='_', bottom: str='_', sides: str='', line_length: int=100):
	def cl(text: str): print(str(color) + sides + text.center(line_length - 2*len(sides)) + sides)
	print(str(color) + top * line_length)
	for line in lines:
		cl(line)
	print(str(color) + bottom * line_length)

