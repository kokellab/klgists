from pathlib import Path
import os, io, shutil, gzip, platform, re
from enum import Enum
from typing import Iterator, Iterable, Mapping

import dill

from klgists.common import pjoin, pexists, pfile, pdir, pdirname, plexists
from klgists.common.exceptions import InvalidDirectoryException, MissingResourceException


class OverwriteChoice(Enum):
	FAIL = 1
	WARN = 2
	IGNORE = 3
	OVERWRITE = 4

def pempty(s: str):
	"""
	Assesses whether the path is "empty" OR does not exist.
	Returns False if the path exists or is either:
		- A socket or block device (even if "empty" -- does not attempt to read)
		- A nonempty file
		- A directory containing subpaths
		- A symlink to a nonempty file
	Currently DOES NOT HANDLE: Symlinks to anything other than a file. Will raise a TypeError.
	"""
	if not pexists(s): return True
	s = Path(s)
	if s.is_block_device() or s.is_socket():
		return False
	elif s.is_dir():
		# short-circuit
		for _ in s.iterdir():
			return False
		return True
	elif s.is_symlink():
		target = Path(os.readlink(str(s)))
		if not target.exists():
			return True
		if target.is_file():
			return s.lstat().st_size == 0
		# TODO if dir without infinite loops
	elif s.is_file():
		return s.stat().st_size == 0
	raise TypeError("Unknown path type {}".format(s))

def fix_path(path: str) -> str:
	# ffmpeg won't recognize './' and will simply not write images!
	# and Python doesn't recognize ~
	if '%' in path: raise ValueError(
		'For technical limitations (regarding ffmpeg), local paths cannot contain a percent sign (%), but "{}" does'.format(path)
	)
	if path == '~': return os.environ['HOME']  # prevent out of bounds
	if path.startswith('~'):
		path = pjoin(os.environ['HOME'], path[2:])
	return path.replace('./', '')

def fix_path_platform_dependent(path: str) -> str:
	"""Modifies path strings to work with Python and external tools.
	Replaces a beginning '~' with the HOME environment variable.
	Also accepts either / or \ (but not both) as a path separator in windows. 
	"""
	path = fix_path(path)
	# if windows, allow either / or \, but not both
	if platform.system() == 'Windows':
		bits = re.split('[/\\\\]', path)
		return pjoin(*bits).replace(":", ":\\")
	else:
		return path


# NTFS doesn't allow these, so let's be safe
# Also exclude control characters
# 127 is the DEL char
_bad_chars = {'/', ':', '<', '>', '"', "'", '\\', '|', '?', '*', chr(127), *{chr(i) for i in range(0, 32)}}
assert ' ' not in _bad_chars
def _sanitize_bit(p: str) -> str:
	for b in _bad_chars: p = p.replace(b, '-')
	return p

def pjoin_sanitized_rel(*pieces: Iterable[any]) -> str:
	"""Builds a path from a hierarchy, sanitizing the path by replacing /, :, <, >, ", ', \, |, ?, *, <DEL>, and control characters 0–32 with a hyphen-minus (-).
	Each input to pjoin_sanitized must refer only to a single directory or file (cannot contain a path separator).
	This means that you cannot have an absolute path (it would begin with os.path (probably /); use pjoin_sanitized_abs for this.
	"""
	return pjoin(*[_sanitize_bit(str(bit)) for bit in pieces])

def pjoin_sanitized_abs(*pieces: Iterable[any]) -> str:
	"""Same as pjoin_sanitized_rel but starts with os.sep (the root directory)."""
	return pjoin(os.sep, pjoin_sanitized_rel(*pieces))


def make_dirs(output_dir: str):
	"""Makes a directory if it doesn't exist.
	May raise a InvalidDirectoryException.
	"""
	# '' can break on Windows
	if output_dir == '': return
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)
	elif not os.path.isdir(output_dir):
		raise InvalidDirectoryException("{} already exists and is not a directory".format(output_dir))


def remake_dirs(output_dir: str):
	"""Makes a directory, remaking it if it already exists.
	May raise a InvalidDirectoryException.
	"""
	if os.path.exists(output_dir) and os.path.isdir(output_dir):
		shutil.rmtree(output_dir)
	elif os.path.exists(output_dir):
		raise InvalidDirectoryException("{} already exists and is not a directory".format(output_dir))
	make_dirs(output_dir)

def replace_in_file(path: str, changes: Mapping[str, str]) -> None:
	"""Uses re.sub repeatedly to modify (AND REPLACE) a file's content."""
	with open(path) as f: data = f.read()
	for key, value in changes.items():
		data = re.sub(key, value, data, re.MULTILINE, re.DOTALL)
	with open(path, 'w', encoding="utf8") as f: f.write(data)


def lines(file_name: str, known_encoding='utf-8') -> Iterator[str]:
	"""Lazily read a text file or gzipped text file, decode, and strip any newline character (\n or \r).
	If the file name ends with '.gz' or '.gzip', assumes the file is Gzipped.
	Arguments:
		known_encoding: Applied only when decoding gzip
	"""
	if file_name.endswith('.gz') or file_name.endswith('.gzip'):
		with io.TextIOWrapper(gzip.open(file_name, 'r'), encoding=known_encoding) as f:
			for line in f: yield line.rstrip('\n\r')
	else:
		with open(file_name, 'r') as f:
			for line in f: yield line.rstrip('\n\r')


def file_from_env_var(var: str) -> str:
	"""
	Just returns the path of a file specified in an environment variable, checking that it's a file.
	Will raise a MissingResourceException error if not set or not a file.
	:param var: The environment variable name, not including the $
	"""
	if var not in os.environ:
		raise MissingResourceException('Environment variable ${} is not set'.format(var))
	config_file_path = fix_path(os.environ[var])
	if not pexists(config_file_path):
		raise MissingResourceException("{} file {} does not exist".format(var, config_file_path))
	if not pfile(config_file_path):
		raise MissingResourceException("{} file {} is not a file".format(var, config_file_path))
	return config_file_path
