import os
from warnings import warn
from typing import Mapping
from klgists.common.exceptions import InvalidFileException


class WindowsPaths:

	@staticmethod
	def sanitize_filename(path: str, show_warnings: bool = True) -> str:
		return WindowsPaths._sanitize(path, True, show_warnings)

	@staticmethod
	def sanitize_directory_name(path: str, show_warnings: bool = True) -> str:
		return WindowsPaths._sanitize(path, False, show_warnings)

	@staticmethod
	def _sanitize(path: str, is_file: bool, show_warnings: bool, sep = os.sep) -> str:
		path = path.strip()
		bad_chars = {
			'<', '>', ':', '"', '|', '?', '*',
			'\\', '/',
			*{chr(c) for c in range(128, 128+33)},
			*{chr(c) for c in range(0, 32)}
		}
		bad_chars = {b: '_' for b in bad_chars}
		bad_strs = {
			'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8',
			'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
			' ', ''
		}
		def fix(bit, i):
			fixed = WindowsPaths._replace_all(bit, bad_chars)
			# allow '.' as the current directory, for directories
			while fixed.endswith(' ') or fixed.endswith('.') and fixed != '.':
				fixed = fixed[:-1]
			if bit.strip() == '':
				raise InvalidFileException("Path {} has a node (#{}) that is empty or contains only whitespace".format(path, i))
			if bit in bad_strs:
				raise InvalidFileException("Path {} has node '{}' (#{}), which is reserved".format(path, bit, i))
			if len(bit) > 254:
				raise InvalidFileException("Path {} has node '{}' (#{}), which has more than 254 characters".format(path, bit, i))
			return fixed
		bits = path.split(sep)
		if path.startswith(sep):
			fixed_bits = ['/', *[fix(bit, i) for i, bit in enumerate(bits) if i > 0]]
		else:
			fixed_bits = [fix(bit, i) for i, bit in enumerate(bits)]
		fixed_bits = [bit for i, bit in enumerate(fixed_bits) if bit != '.' or i==0]
		new_path = os.path.join(*fixed_bits)
		# never allow '.' or ' ' to end a filename
		while new_path.endswith(' ') or new_path.endswith('.'):
			new_path = new_path[:-1]
		if new_path != path and show_warnings:
			warn("Sanitized filename {} → {}".format(path, new_path))
		return new_path

	@staticmethod
	def _replace_all(s: str, rep: Mapping[str, str]) -> str:
		for k, v in rep.items():
			s = s.replace(k, v)
		return s

	def __repr__(self): return self.__class__.__name__
	def __str__(self): return self.__class__.__name__


__all__ = ['WindowsPaths']
