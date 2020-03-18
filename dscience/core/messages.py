from enum import Enum
from typing import Mapping

class MsgLevel(Enum):
	INFO = 1
	SUCCESS = 2
	NOTICE = 3
	WARNING = 4
	FAILURE = 5


class MsgFormatter:
	def __call__(self, message: str, level: MsgLevel) -> str:
		raise NotImplementedError()


class MsgFormatterSimple(MsgFormatter):

	def __init__(self, prefixes: Mapping[MsgLevel, str], suffixes: Mapping[MsgLevel, str]):
		self.prefixes, self.suffixes = prefixes, suffixes

	def __call__(self, message: str, level: MsgLevel) -> str:
		return self.prefixes.get(level, '') + message + self.suffixes.get(level, '')


__all__ = ['MsgLevel', 'MsgFormatter', 'MsgFormatterSimple']

