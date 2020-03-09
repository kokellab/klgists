from typing import Mapping, Callable, Union, Any
from datetime import datetime
import logging
from pathlib import PurePath, Path
from copy import deepcopy
from IPython.core.magic import line_magic, magics_class, Magics
from IPython import get_ipython
from dscience.core.exceptions import InvalidFileError
logger = logging.getLogger('dscience')

class TemplateParser:
	def __init__(self, entries: Mapping[str,  Union[Any, Callable[[None], str]]]):
		self.entries = deepcopy(entries)

	def fill(self, r: str):
		for k, v in self.entries.items():
			k = '${{' + k + '}}'
			if k in r:
				try:
					r = r.replace(k, v())
				except Exception:
					logger.error("Failed replacing {}".format(k))
		return r

	@classmethod
	def standard(cls, semantic_version: str, **extra):
		now = datetime.now()
		'''
		'hash': lambda: Tools.git_commit_hash(kale_env.home),
			'username': lambda: kale_env.username,
			'author': lambda: kale_env.username.title(),
			'config': lambda: kale_env.config_file
		'''
		return TemplateParser({
			'version': lambda: semantic_version,
			'major': lambda: semantic_version.split('.')[0],
			'minor': lambda: semantic_version.split('.')[1],
			'patch': lambda: semantic_version.split('.')[2],
			'datestr': lambda: str(now.date()),
			'timestr': lambda: str(now.time()),
			'datetuple': lambda: str((now.year, now.month, now.day)),
			'datetime': lambda: str((now.year, now.month, now.day, now.hour, now.minute, now.second)),
			**extra
		})

@magics_class
class TemplateMagic(Magics):
	def __init__(self, shell, template_path: Union[PurePath, str], processor: TemplateParser):
		super().__init__(shell)
		self.template_path = Path(template_path)
		self.processor = processor

	@line_magic
	def fill(self, line):
		path = self.template_path
		if not path.exists():
			raise InvalidFileError("Jupyter template text file at {} does not exist".format(path), path=path)
		text = self.processor.fill(path.read_text(encoding='utf-8'))
		self.shell.set_next_input(text, replace=True)

	@classmethod
	def from_template_path(cls, path: Union[PurePath, str], processor: TemplateParser):
		data = Path(path).read_text(encoding='utf8')
		return TemplateMagic(get_ipython(), data, processor)


__all__ = ['TemplateMagic']
