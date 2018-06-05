import logging
import os
import warnings
import hashlib
from klgists.files.file_hasher import FileHasher
from klgists.files import OverwriteChoice
from klgists.common import pexists, pdir, pjoin, pfile
from klgists.common.exceptions import NoSuchDirectoryException, PathIsNotDirectoryException, PathIsNotFileException, PathAlreadyExistsException
from klgists.files.wrap_cmd_call import wrap_cmd_call


def sevenz(dir_to_sevenz: str, sevenz_path: str, overwrite: OverwriteChoice = OverwriteChoice.FAIL, _7z_executable: str = '7z') -> None:
	"""7-zips a directory and adds a .sha256 with the same base filename of the output archive.
	Leaves the original directory when it finishes.
	Requires '7z' to be on the command line.
	"""
	if not pexists(dir_to_sevenz):
		raise NoSuchDirectoryException("The path {} to 7-zip does not exist".format(dir_to_sevenz))
	if not pdir(dir_to_sevenz):
		raise PathIsNotDirectoryException("The path {} to 7-zip is not a directory".format(dir_to_sevenz))

	file_hasher = FileHasher(algorithm=hashlib.sha256, extension='.sha256')
	logging.info("7-zipping files in {}".format(dir_to_sevenz))

	if pexists(sevenz_path) and not pfile(sevenz_path):
		raise PathIsNotFileException("The 7-zip file cannot be written to {}: The path exists and is not a file".format(sevenz_path))

	if pexists(sevenz_path):
		if overwrite is OverwriteChoice.FAIL:
			raise PathAlreadyExistsException("Cannot proceed: The 7-zip file {} already exists.".format(sevenz_path))
		elif overwrite is OverwriteChoice.WARN:
			warnings.warn("The 7-zip file {} already exists. Won't overwrite.".format(sevenz_path))
		elif overwrite is OverwriteChoice.OVERWRITE:
			os.remove(sevenz_path)
		elif overwrite is OverwriteChoice.IGNORE:
			pass

	wrap_cmd_call([_7z_executable, 'a', sevenz_path, dir_to_sevenz])
	file_hasher.add_hash(sevenz_path)  # will overwrite regardless
