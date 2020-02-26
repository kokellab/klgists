from typing import Collection, TypeVar, Iterator, Union, Callable, Optional, Iterable, Any
from datetime import datetime
import time
import logging
from dscience_gists.tools.base_tools import BaseTools
from dscience_gists.tools.unit_tools import UnitTools
logger = logging.getLogger('dscience_gists')
T = TypeVar('T')

class LoopTools(BaseTools):

	@classmethod
	def loop(
			cls,
			things: Iterable[T], log: Union[None, str, Callable[[str], None]] = None,
			every_i: int = 10,
			n_total: Optional[int] = None
	) -> Iterator[T]:
		log = cls.get_log_function(log)
		if hasattr(things, '__len__') or n_total is not None:
			# noinspection PyTypeChecker
			yield from cls._loop_timing(things, log, every_i, n_total)
		else:
			yield from cls._loop_logging(things, log, every_i)

	@classmethod
	def _loop_logging(
			cls,
			things: Iterable[T],
			log: Union[None, str, Callable[[str], None]] = None,
			every_i: int = 10
	) -> Iterator[T]:
		log = cls.get_log_function(log)
		initial_start_time = time.monotonic()
		now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		log("Started processing at {}.\n".format(now))
		i = 0
		for i, thing in enumerate(things):
			t0 = time.monotonic()
			yield thing
			t1 = time.monotonic()
			if i % every_i == 0:
				log("Processed {} in {}.\n".format(every_i, UnitTools.delta_time_to_str(t1 - t0)))
		now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		log("Processed {}/{} in {}. Done at {}.\n".format(i, i, UnitTools.delta_time_to_str(time.monotonic() - initial_start_time), now))

	@classmethod
	def _loop_timing(
			cls,
			things: Collection[Any], log: Union[None, str, Callable[[str], None]] = None,
			every_i: int = 10,
			n_total: Optional[int] = None
	):
		log = cls.get_log_function(log)
		n_total = len(things) if n_total is None else n_total
		now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		log("Started processing {} items at {}.\n".format(n_total, now))
		t0 = time.monotonic()
		initial_start_time = time.monotonic()
		for i, thing in enumerate(things):
			yield thing
			t1 = time.monotonic()
			if i % every_i == 0 and i < n_total - 1:
				estimate = (t1 - initial_start_time) / (i + 1) * (n_total - i - 1)
				log(
					"Processed {}/{} in {}. Estimated {} left.\n"
					.format(i + 1, n_total, UnitTools.delta_time_to_str(t1 - t0), UnitTools.delta_time_to_str(estimate))
				)
		now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		delta = UnitTools.delta_time_to_str(time.monotonic() - initial_start_time)
		log("Processed {}/{} in {}. Done at {}.\n".format(n_total, n_total, delta, now))

	@classmethod
	def parallel(cls, items, function, n_cores: int = 2) -> None:
		import itertools
		import multiprocessing
		t0 = time.monotonic()
		print("\n[{}] Using {} cores...".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), n_cores))
		with multiprocessing.Pool(n_cores) as pool:
			queue = multiprocessing.Manager().Queue()
			result = pool.starmap_async(function, items)
			cycler = itertools.cycle('\\|/―')
			while not result.ready():
				print("Percent complete: {:.0%} {}".format(queue.qsize() / len(items), next(cycler)), end='\r')
				time.sleep(0.4)
			got = result.get()
		print("\n[{}] Processed {} items in {:.1f}s".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), len(got), time.monotonic() - t0))


__all__ = ['LoopTools']
