import os, io, shutil, gzip
from enum import Enum
from typing import Iterator

from klgists.common import pjoin


class OverwriteChoice(Enum):
	FAIL = 1
	WARN = 2
	IGNORE = 3
	OVERWRITE = 4


def fix_path(path: str) -> str:
	"""Modifies path strings to work with Python and external tools.
	Replaces a beginning '~' with the HOME environment variable.
	"""
	# ffmpeg won't recognize './' and will simply not write images!
	# and Python doesn't recognize ~
	if '%' in path: raise ValueError(
		'For technical limitations (regarding ffmpeg), local paths cannot contain a percent sign (%), but "{}" does'.format(path)
	)
	if path == '~': return os.environ['HOME']  # prevent out of bounds
	if path.startswith('~'):
		path = pjoin(os.environ['HOME'], path[2:])
	return path.replace('./', '')


from klgists.common.exceptions import PathIsNotDirectoryException


def make_dirs(output_dir: str):
	"""Makes a directory if it doesn't exist.
	May raise a PathIsNotDirectoryException.
	"""
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)
	elif not os.path.isdir(output_dir):
		raise PathIsNotDirectoryException("{} already exists and is not a directory".format(output_dir))


def remake_dirs(output_dir: str):
	"""Makes a directory, remaking it if it already exists.
	May raise a PathIsNotDirectoryException.
	"""
	if os.path.exists(output_dir) and os.path.isdir(output_dir):
		shutil.rmtree(output_dir)
	elif os.path.exists(output_dir):
		raise PathIsNotDirectoryException("{} already exists and is not a directory".format(output_dir))
	make_dirs(output_dir)



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

import dill

def pkl(data, path: str):
	with open(path, 'wb') as f:
		dill.dump(data, f)

def unpkl(path: str):
	with open(path, 'rb') as f:
		return dill.load(f)
