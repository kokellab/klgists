import os
import shutil

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