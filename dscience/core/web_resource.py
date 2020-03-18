from urllib import request
import zipfile
import logging
import gzip
import enum
import shutil
from typing import Optional, Mapping
from datetime import datetime
from pathlib import Path
from dscience.core.internal import PathLike
from dscience.core.abcd import *
logger = logging.getLogger('dscience')

@enum.unique
class ArchiveType(enum.Enum):
	FLAT = 1
	ZIP = 2
	TAR = 3
	TARGZ = 4

@auto_eq()
@auto_hash()
class WebResource:
	"""
	Useful for extracting files from ZIP and GZIPing them.
	"""
	def __init__(self, url: str, archive_member: Optional[str], local_path: PathLike):
		self._url, self._archive_member, self._local_path = url, archive_member, Path(local_path)

	def download(self, redownload: bool = False):
		now = datetime.now()
		to_path = Path(self._local_path)
		if not to_path.exists() or redownload:
			extracted, dled = None, None
			try:
				logger.info("Downloading {}...".format(self._url))
				tmp = str(to_path) + now.strftime('%Y%m%d-%H%M%S-%f') + '.tmp'
				dled, response = request.urlretrieve(self._url, tmp)
				dled = Path(dled)
				if self._archive_member is not None:
					with zipfile.ZipFile(dled, 'r') as zfile:
						extracted = Path(zfile.extract(self._archive_member))
				else:
					extracted = dled
				if to_path.suffix == '.gz' and not self.__is_gzip(extracted):
					with extracted.open('rb') as f_in:
						with gzip.open(to_path, 'wb') as f_out:
							shutil.copyfileobj(f_in, f_out)
				else:
					shutil.move(extracted, to_path)
				self._info_path.write_text('url='+self._url+'\n' + 'datetime_downloaded='+now.isoformat()+'\n' + 'response='+str(response).replace('\n', ' |')+'\n')
			finally:
				if extracted is not None and extracted.exists():
					extracted.unlink()
				if dled is not None and dled.exists():
					dled.unlink()
			print(to_path, to_path.exists())

	def datetime_downloaded(self) -> datetime:
		return datetime.fromisoformat(self.metadata()['datetime_downloaded'])

	def metadata(self) -> Mapping[str, str]:
		return {
			line[:line.index('=')].strip(): line[line.index('=')+1:].strip()
			for line in self._info_path.read_text(encoding='utf8').splitlines()
		}

	@property
	def _info_path(self) -> Path:
		return self._local_path.with_suffix(self._local_path.suffix + '.info')

	def exists(self) -> bool:
		return self._local_path.exists()

	@property
	def path(self) -> Path: return self._local_path

	def delete(self) -> bool:
		if self.exists:
			self.path.unlink()
			self._info_path.unlink()
			return True
		else:
			return False

	def __is_gzip(self, path):
		try:
			with gzip.open(path, 'rb') as f:
				f.read(20)  # 10-byte header
		except OSError as e:
			if 'Not a gzipped file' in str(e):
				return False
			else:
				raise e
		return True


__all__ = ['WebResource']
