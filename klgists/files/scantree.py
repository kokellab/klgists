import os
import typing
from typing import Iterator, Optional, Callable, Set


def is_proper_file(path: str) -> bool:
	name = os.path.split(path)[1]
	return len(name) > 0 and name[0] not in {'.', '~', '_'}


def scantree(path: str, follow_symlinks: bool=False) -> Iterator[str]:
	"""List the full path of every file not beginning with '.', '~', or '_' in a directory, recursively.
	.. deprecated Use scan_for_proper_files, which has a better name
	"""
	for entry in os.scandir(path):
		if entry.is_dir(follow_symlinks=follow_symlinks):
			yield from scantree(entry.path)
		elif is_proper_file(entry.path):
			yield entry.path


def scan_for_files(path: str, follow_symlinks: bool=False) -> Iterator[str]:
	"""
	Using a generator, list all files in a directory or one of its subdirectories.
	Useful for iterating over files in a directory recursively if there are thousands of file.
	Warning: If there are looping symlinks, follow_symlinks will return an infinite generator.
	"""
	for d in os.scandir(path):
		if d.is_dir(follow_symlinks=follow_symlinks):
			yield from scan_for_files(d.path)
		else:
			yield d.path


def walk_until(some_dir, until: Callable[[str], bool]) -> Iterator[typing.Tuple[str, str, str]]:
	"""Walk but stop recursing after 'until' occurs.
	Returns files and directories in the same manner as os.walk
	"""
	some_dir = some_dir.rstrip(os.path.sep)
	assert os.path.isdir(some_dir)
	for root, dirs, files in os.walk(some_dir):
			yield root, dirs, files
			if until(root):
					del dirs[:]


def walk_until_level(some_dir, level: Optional[int]=None) -> Iterator[typing.Tuple[str, str, str]]:
	"""
	Walk up to a maximum recursion depth.
	Returns files and directories in the same manner as os.walk
	Taken partly from https://stackoverflow.com/questions/7159607/list-directories-with-a-specified-depth-in-python
	:param some_dir:
	:param level: Maximum recursion depth, starting at 0
	"""
	some_dir = some_dir.rstrip(os.path.sep)
	assert os.path.isdir(some_dir)
	num_sep = some_dir.count(os.path.sep)
	for root, dirs, files in os.walk(some_dir):
			yield root, dirs, files
			num_sep_this = root.count(os.path.sep)
			if level is None or num_sep + level <= num_sep_this:
					del dirs[:]


def delete_hidden_files(directory: str, filename_starts: Optional[Set[str]] = None) -> None:
	"""Deletes any files beginning with '.' or '~'"""
	if filename_starts is None: filename_starts = {'.', '~'}
	for f in scan_for_files(directory):
		for s in filename_starts:
			if os.path.basename(f).startswith(s): os.remove(f)


__all__ = ['scan_for_files', 'walk_until', 'walk_until_level']
