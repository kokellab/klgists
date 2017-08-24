import os
from typing import Set, Optional
from klgists.files.scantree import scan_for_files

def delete_hidden_files(directory: str, filename_starts: Optional[Set[str]] = None) -> None:
	"""Deletes any files beginning with '.' or '~'"""
	if filename_starts is None: filename_starts = {'.', '~'}
	for f in scan_for_files(directory):
		for s in filename_starts:
			if os.path.basename(f).startswith(s): os.remove(f)

