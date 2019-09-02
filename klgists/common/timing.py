import sys, time, logging
from datetime import datetime
from typing import Iterable, Optional, Iterator, Collection, Any, TypeVar, Callable, Union
from klgists.common import DelegatingWriter, get_log_function
logger = logging.getLogger('klgists')

T = TypeVar('T')


class TimingTools:

	@staticmethod
	def delta_time_to_str(delta_sec: float) -> str:
		"""
		Returns a pretty string from a difference in time in seconds.
		:param delta_sec: The time in seconds
		:return: A string with units 'hr', 'min', or 's'
		"""
		if abs(delta_sec) > 60*60*3:
			return str(round(delta_sec/60/60, 2)) + 'hr'
		elif abs(delta_sec) > 180:
			return str(round(delta_sec/60, 2)) + 'min'
		else:
			return str(round(delta_sec, 1)) + 's'

	@staticmethod
	def ms_to_minsec(ms: int) -> str:
		"""
		Converts a number of milliseconds to one of the following formats:
			- 10ms         if < 1 sec
			- 10:15        if < 1 hour
			- 10:15:33     if < 1 day
			- 5d:10:15:33  if > 1 day
		Prepends a minus sign (−) if negative.
		:param ms: The milliseconds
		:return: A string of one of the formats above
		"""
		is_neg = ms < 0
		ms = abs(int(ms))
		seconds = int((ms/1000) % 60)
		minutes = int((ms/(1000*60)) % 60)
		hours = int((ms/(1000*60*60)) % 24)
		days = int(ms/(1000*60*60*24))
		if ms < 1000:
			s = "{}ms".format(ms)
		elif days > 1:
			s = "{}d:{}:{}:{}".format(days, str(hours).zfill(2), str(minutes).zfill(2), str(seconds).zfill(2))
		elif hours > 1:
			s = "{}:{}:{}".format(str(hours).zfill(2), str(minutes).zfill(2), str(seconds).zfill(2))
		else:
			s = "{}:{}".format(str(minutes).zfill(2), str(seconds).zfill(2))
		return '−' + s if is_neg else s

	@staticmethod
	def loop(things: Iterable[T], log: Union[None, str, Callable[[str], None]] = None, every_i: int = 10, n_total: Optional[int] = None) -> Iterator[T]:
		log = get_log_function(log)
		if hasattr(things, '__len__') or n_total is not None:
			# noinspection PyTypeChecker
			yield from TimingTools.loop_timing(things, log, every_i, n_total)
		else:
			yield from TimingTools.loop_logging(things, log, every_i)

	@staticmethod
	def loop_logging(things: Iterable[T], log: Union[None, str, Callable[[str], None]] = None, every_i: int = 10) -> Iterator[T]:
		log = get_log_function(log)
		initial_start_time = time.monotonic()
		now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		log("Started processing at {}.\n".format(now))
		try:
			i = 0
			for thing in things:
				t0 = time.monotonic()
				yield thing
				t1 = time.monotonic()
				if i % every_i == 0:
					log("Processed {} in {}.\n".format(every_i, TimingTools.delta_time_to_str(t1 - t0)))
				i += 1
			now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			log("Processed {}/{} in {}. Done at {}.\n".format(i, i, TimingTools.delta_time_to_str(
				time.monotonic() - initial_start_time), now))
		finally:
			if none is not None: none.close()

	@staticmethod
	def loop_timing(things: Collection[Any], log: Union[None, str, Callable[[str], None]] = None, every_i: int = 10, n_total: Optional[int] = None):
		log = get_log_function(log)
		n_total = len(things) if n_total is None else n_total
		now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		log("Started processing {} items at {}.\n".format(n_total, now))
		t0 = time.monotonic()
		try:
			initial_start_time = time.monotonic()
			for i, thing in enumerate(things):
				yield thing
				t1 = time.monotonic()
				if i % every_i == 0 and i < n_total - 1:
					estimate = (t1 - initial_start_time) / (i + 1) * (n_total - i - 1)
					log("Processed {}/{} in {}. Estimated {} left.\n".format(i + 1, n_total, TimingTools.delta_time_to_str(t1 - t0), TimingTools.delta_time_to_str(estimate)))
			now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			delta = TimingTools.delta_time_to_str(time.monotonic() - initial_start_time)
			log("Processed {}/{} in {}. Done at {}.\n".format(n_total, n_total,delta, now))
		finally:
			if none is not None: none.close()

	def __repr__(self): return self.__class__.__name__
	def __str__(self): return self.__class__.__name__


__all__ = ['TimingTools']
