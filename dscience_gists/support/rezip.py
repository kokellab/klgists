import wget
import zipfile
import os
import logging
import gzip
import shutil
from pathlib import Path, PurePath
from typing import Optional, Union

logger = logging.getLogger('dscience_gists')


class Rezipper:

	def gz(self, input_filename: Union[str, PurePath], output_filename: Union[None, str, PurePath] = None):
		"Gzips a file, by default to input_filename + '.gz'."
		input_filename = Path(input_filename)
		if output_filename is None:
			output_filename = Path(str(input_filename) + '.gz')
		with input_filename.open('rb') as f_in:
			with gzip.open(output_filename, 'wb') as f_out:
				shutil.copyfileobj(f_in, f_out)

	def rezip(self, input_filename: str, output_filename_base: str):
		"""Gzips a file. If input_filename ends in '.zip', extracts output_filename_base from the ZIP archive.
		In every case, writes the gzipped file to output_filename_base + '.gz'.
		Warning: Deletes the original input file.
		"""
		tmp_filename = input_filename  # set in if
		if input_filename.endswith('.zip'):
			with zipfile.ZipFile(input_filename, 'r') as zfile:
				zfile.extract(output_filename_base)
				tmp_filename = output_filename_base
		# It's gzipped iff the original had a .gz
		if not tmp_filename.endswith('.gz'):
			self.gz(output_filename_base)
		os.remove(tmp_filename)
		if os.path.exists(input_filename):
			os.remove(input_filename)

	def dl_and_rezip(self, url: str, base_filename: str):
		"""Downloads a file and gzips it. If the download file is a ZIP archive, first extracts base_filename from it.
		The gzipped output file is written to base_filename + '.gz'."""
		if not os.path.exists(base_filename + '.gz'):
			logger.info("Downloading {}...".format(url))
			dled_filename = wget.download(url)
			self.rezip(dled_filename, base_filename)
			logger.info("Done—file at {}".format(base_filename))


__all__ = ['Rezipper']
