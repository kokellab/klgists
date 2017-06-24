import logging
import warnings
import shutil
from klgists.common import pexists, pjoin
from klgists.files.file_hasher import FileHasher
from klgists.files.wrap_cmd_call import wrap_cmd_call

def sevenz(dir_to_sevenz: str, sevenz_path: str]) -> None:
	"""7-zips a directory and adds a .sha256 with the same base filename of the output archive.
	Will warn and not overwrite if the archive already exists.
	Warning: Deletes the original directory when it finishes.
	Requires '7z' to be on the command line.
	"""
	file_hasher = FileHasher(algorithm=hashlib.sha256, extension='.sha256')
	logging.info("7-zipping files in {}".format(dir_to_sevenz))
	pexists(sevenz_filename):
		warnings.warn("The 7-zip file {} already exists. Won't overwrite.".format(sevenz_filename))
	else:
		wrap_cmd_call(['7z', 'a', sevenz_filename, pjoin(dir_to_sevenz, '*.*')])
		shutil.rmtree(dir_to_sevenz)
	file_hasher.add_hash(sevenz_filename)  # will overwrite
