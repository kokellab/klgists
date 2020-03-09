import os, sys
import logging
from pathlib import Path
from typing import Mapping
from dscience_gists.tools.base_tools import BaseTools
from dscience_gists.core import PathLike
from dscience_gists.core.exceptions import BadCommandError, InvalidDirectoryError, InvalidFileError, ContradictoryArgumentsError
logger = logging.getLogger('dscience_gists')


class PathTools(BaseTools):

	@classmethod
	def guess_trash(cls) -> Path:
		"""
		Chooses a reasonable path for trash based on the OS.
		This is not reliable. For a more sophisticated solution, see https://github.com/hsoft/send2trash
		However, even that can fail.
		"""
		plat = sys.platform.lower()
		if 'darwin' in plat:
			return Path.home() / '.Trash'
		elif 'win' in plat:
			return Path(Path.home().root) / '$Recycle.Bin'
		else:
			return Path.home() / '.trash'

	@classmethod
	def prep_dir(cls, path: PathLike, exist_ok: bool) -> bool:
		"""
		Prepares a directory by making it if it doesn't exist.
		If exist_ok is False, calls logger.warning it already exists
		"""
		path = Path(path)
		exists = path.exists()
		# On some platforms we get generic exceptions like permissions errors, so these are better
		if exists and not path.is_dir():
			raise InvalidDirectoryError("Path {} exists but is not a file".format(path))
		if exists and not exist_ok:
			logger.warning("Directory {} already exists".format(path))
		if not exists:
			# NOTE! exist_ok in mkdir throws an error on Windows
			path.mkdir(parents=True)
		return exists

	@classmethod
	def prep_file(cls, path: PathLike, overwrite: bool = True, append: bool = False) -> bool:
		"""
		Prepares a file path by making its parent directory (if it doesn't exist) and checking it.
		"""
		# On some platforms we get generic exceptions like permissions errors, so these are better
		path = Path(path)
		exists = path.exists()
		if overwrite and append:
			raise ContradictoryArgumentsError("Can't append and overwrite file {}".format(path))
		if exists and not overwrite and not append:
			raise FileExistsError("Path {} already exists".format(path))
		elif exists and not path.is_file() and not path.is_symlink():  # TODO check link?
			raise InvalidFileError("Path {} exists but is not a file".format(path))
		# NOTE! exist_ok in mkdir throws an error on Windows
		if not path.parent.exists():
			Path(path.parent).mkdir(parents=True, exist_ok=True)
		return exists

	@classmethod
	def sanitize_file_path(cls, path: str, show_warnings: bool = True) -> Path:
		return cls._sanitize(path, True, show_warnings)

	@classmethod
	def sanitize_directory_path(cls, path: str, show_warnings: bool = True) -> Path:
		return cls._sanitize(path, False, show_warnings)

	@staticmethod
	def sanitize_prepped_file_path(path: PathLike, show_warnings: bool = True) -> Path:
		"""It's ok for the file to exist."""
		path = Path(PathTools.sanitize_file_path(path, show_warnings))
		PathTools.prep_file(path, True, False)
		return path

	@classmethod
	def _sanitize(cls, path: str, is_file: bool, show_warnings: bool, sep = os.sep) -> Path:
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
			fixed = cls._replace_all(bit, bad_chars)
			# allow '.' as the current directory, for directories
			while fixed.endswith(' ') or fixed.endswith('.') and fixed != '.':
				fixed = fixed[:-1]
			if bit.strip() == '':
				raise InvalidFileError("Path {} has a node (#{}) that is empty or contains only whitespace".format(path, i))
			if bit in bad_strs:
				raise InvalidFileError("Path {} has node '{}' (#{}), which is reserved".format(path, bit, i))
			if len(bit) > 254:
				raise InvalidFileError("Path {} has node '{}' (#{}), which has more than 254 characters".format(path, bit, i))
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
			logger.warning("Sanitized filename {} → {}".format(path, new_path))
		return Path(new_path)

	@classmethod
	def _replace_all(cls, s: str, rep: Mapping[str, str]) -> str:
		for k, v in rep.items():
			s = s.replace(k, v)
		return s


__all__ = ['PathTools']
