import os
from typing import Callable, Iterator

from klgists.files.scantree import scan_for_files
from klgists.common.exceptions import MultipleMatchesException, NoSuchPathException, PathIsNotDirectoryException, NoSuchDirectoryException


def find_only_file_matching(directory: str, matcher: Callable[[str], bool], file_iterator: Callable[[str], Iterator[str]]=scan_for_files) -> str:
	"""Returns the full path of the matching file and raises an exception if none are found or more than 1 is found."""
	if os.path.exists(directory) and not os.path.isdir(directory):
		raise PathIsNotDirectoryException("Cannot look under {}: Not a directory".format(directory))
	if not os.path.exists(directory):
		raise NoSuchDirectoryException("Cannot look under {}: Does not exist".format(directory))
	file = None
	for f in file_iterator(directory):
		if matcher(f):
			if file is not None:
				raise MultipleMatchesException("Multiple matching files found in {}".format(directory))
			file = f
	if file is None:
		raise NoSuchPathException("No matching file found in {}".format(directory))
	return file
