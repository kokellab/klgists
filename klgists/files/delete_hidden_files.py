import os
from klgists.files.scantree import scan_for_files

def delete_hidden_files(directory: str) -> None:
	"""Deletes any files beginning with '.' or '~'"""
	for f in scan_for_files(directory):
		if os.path.basename(f).startswith('.') or os.path.basename(f).startswith('~'):
			os.remove(f)

