import os
from enum import Enum

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
