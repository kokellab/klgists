from urllib import request
import zipfile
import logging
import gzip
import shutil
from pathlib import Path
from dscience.core.internal import PathLike
logger = logging.getLogger('dscience')


class Rezipper:
	"""
	Useful for extracting files from ZIP and GZIPing them.
	"""

	def dl_and_rezip(self, url: str, outfile: PathLike) -> Path:
		"""
		Downloads a file and gzips it. If the download file is a ZIP archive, first extracts outfile from it.
		The gzipped output file is written to outfile + '.gz'."""
		outfile = Path(outfile)
		finalpath = outfile.with_suffix(outfile.suffix + '.gz')
		if not outfile.exists():
			logger.info("Downloading {}...".format(url))
			dled_filename = request.urlretrieve(url)
			self.rezip(dled_filename, outfile)
			logger.info("Done—file at {}".format(finalpath))
		return finalpath

	def rezip(self, infile: PathLike, outfile: PathLike) -> Path:
		"""
		Gzips a file. If input_filename ends in '.zip', extracts outfile from the ZIP archive.
		Writes to `outfile + '.gz'
		Warning: Deletes the original input file when done.
		"""
		infile, outfile = Path(infile), Path(outfile)
		tmpfile = infile  # set in if
		if infile.suffix == '.zip':
			with zipfile.ZipFile(infile, 'r') as zfile:
				zfile.extract(outfile)
				tmpfile = outfile
		# It's gzipped iff the original had a .gz
		if tmpfile.suffix != '.gz':
			self.gz(outfile)
			tmpfile.unlink()
		if infile.exists():
			infile.unlink()
		return outfile.with_suffix(outfile.suffix + '.gz')

	def gz(self, infile: PathLike, outfile: PathLike = None):
		"""Gzips a file, by default to input_filename + '.gz'."""
		infile = Path(infile)
		outfile = Path(infile.with_suffix(infile.suffix + '.gz')) if outfile is None else Path(outfile)
		with infile.open('rb') as f_in:
			with gzip.open(outfile, 'wb') as f_out:
				shutil.copyfileobj(f_in, f_out)


__all__ = ['Rezipper']
