from __future__ import annotations
from functools import total_ordering
from typing import Union


@total_ordering
class TimeUnit:
	def __init__(self, unit: str, abbrev: str, singlular: str, n_ms: int):
		self.unit, self.abbrev, self.singular, self.plural, self.n_ms = unit, abbrev, singlular, singlular + 's', n_ms
	def to_ms(self, n: int): return n * self.n_ms
	def __eq__(self, other): return self.n_ms == other.n_ms
	def __lt__(self, other): return self.n_ms < other.n_ms
	def __repr__(self): return '⟨'+self.abbrev+'⟩'
	def __str__(self): return '⟨'+self.abbrev+'⟩'


class TimeUnits:
	MS = TimeUnit('ms', 'ms', 'millisecond', 1)
	SEC = TimeUnit('s', 'sec', 'second', 1000)
	MIN = TimeUnit('min', 'min', 'minute', 60 * 1000)
	HOUR = TimeUnit('hr', 'hour', 'hour', 60 * 60 * 1000)
	DAY = TimeUnit('day', 'day', 'day', 24 * 60 * 60 * 1000)
	WEEK = TimeUnit('wk', 'week', 'week', 24 * 60 * 60 * 1000)

	@classmethod
	def values(cls):
		return [TimeUnits.MS, TimeUnits.SEC, TimeUnits.MIN, TimeUnits.HOUR, TimeUnits.DAY, TimeUnits.WEEK]

	@classmethod
	def of(cls, s: Union[TimeUnit, str]) -> TimeUnit:
		if isinstance(s, TimeUnit):
			return s
		s = s.lower().strip()
		for u in TimeUnits.values():
			if s in [u.abbrev, u.plural, u.singular, u.unit]:
				return u
		raise LookupError("Unit type {} not found".format(s))


__all__ = ['TimeUnit', 'TimeUnits']
