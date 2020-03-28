from __future__ import annotations
from typing import Mapping, Callable, Union, Any, Optional, Generic, TypeVar, Type
from datetime import datetime
import logging
from pathlib import PurePath, Path
from dscience.core.exceptions import FileDoesNotExistError
from dscience.core import PathLike, LazyWrap
logger = logging.getLogger('dscience')


class MagicTemplate:

	@classmethod
	def from_path(cls, path: PathLike, encoding: str = 'utf8', prefix: str = '${{', suffix: str = '}}') -> MagicTemplate:
		return MagicTemplate(lambda: Path(path).read_text(encoding=encoding), prefix=prefix, suffix=suffix)

	@classmethod
	def from_text(cls, text: str, prefix: str = '${{', suffix: str = '}}') -> MagicTemplate:
		return MagicTemplate(lambda: text, prefix=prefix, suffix=suffix)

	def __init__(self, reader: Callable[[], str], prefix: str = '${{', suffix: str = '}}'):
		self._reader = reader
		self._entries = {}
		self._prefix, self._suffix = prefix, suffix

	def add(self, key: str, value: Union[Any, Callable[[str], str]]) -> MagicTemplate:
		self._entries[key] = value
		return self

	def add_version(self, semantic_version: str) -> MagicTemplate:
		self._entries.update({
			'version': semantic_version,
			'major': semantic_version.split('.')[0],
			'minor': semantic_version.split('.')[1] if semantic_version.count('.')>0 else '-',
			'patch': semantic_version.split('.')[2] if semantic_version.count('.')>1 else '-',
		})
		return self

	def add_datetime(self, at: Optional[datetime] = None):
		if at is None:
			now = LazyWrap.new_type('datetime', datetime.now)()
		else:
			now = LazyWrap.new_type('datetime', lambda: at)()
		self._entries.update({
			'year': lambda _: str(now.get().year),
			'month': lambda _: str(now.get().month),
			'day': lambda _: str(now.get().day),
			'hour': lambda _: str(now.get().hour),
			'minute': lambda _: str(now.get().minute),
			'second': lambda _: str(now.get().second),
			'datestr': lambda _: str(now.get().date()),
			'timestr': lambda _: str(now.get().time()),
			'datetuple': lambda _: str((now.get().year, now.get().month, now.get().day)),
			'datetime': lambda _: str((now.get().year, now.get().month, now.get().day, now.get().hour, now.get().minute, now.get().second)),
		})
		return self

	def register_magic(self, name: str, shell = None) -> None:
		from IPython import get_ipython
		if shell is None: shell = get_ipython()
		shell.register_magic_function(self._fill, magic_name=name)

	def parse(self, line: str = '') -> str:
		return self.__replace(self._reader(), line)

	def _fill(self, line, shell):
		text = self.__replace(self._reader(), line)
		shell.set_next_input(text, replace=True)

	def __replace(self, r: str, line: str):
		for k, v in self._entries.items():
			k = self._prefix + k + self._suffix
			if k in r:
				try:
					if callable(v):
						r = r.replace(k, v(line))
					else:
						r = r.replace(k, str(v))
				except Exception:
					logger.error("Failed replacing {}".format(k))
					raise
		return r


__all__ = ['MagicTemplate']
