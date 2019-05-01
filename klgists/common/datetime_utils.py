from datetime import datetime, timedelta
from typing import Tuple

def mkdatetime(s: str) -> datetime:
	return datetime.strptime(s.replace(' ', 'T'), "%Y-%m-%dT%H:%M:%S")

def now() -> datetime:
	return datetime.now()

def today() -> datetime:
	return datetime.today()

def mkdate(s: str) -> datetime:
	return datetime.strptime(s, "%Y-%m-%d")

def this_year(s: str) -> datetime:
	return datetime.strptime(s, "%Y")

def year_range(year: int) -> Tuple[datetime, datetime]:
	return (
		datetime(year, 1, 1, 0, 0, 0, 0),
		datetime(year, 12, 31, 23, 59, 59, 999)
	)

def format_time(time: datetime) -> str:
	"""Standard timestamp format. Ex: 2016-05-02_22_35_56."""
	return time.strftime("%Y-%m-%d_%H-%M-%S")

def timestamp() -> str:
	"""Standard timestamp of time now. Ex: 2016-05-02_22_35_56."""
	return format_time(datetime.now())

def timestamp_path(path: str) -> str:
	"""Standard way to label a file path with a timestamp."""
	return "{}-{}".format(path, timestamp())


def nice_time(n_ms: int) -> str:
	length = datetime(1, 1, 1) + timedelta(milliseconds=n_ms)
	if n_ms < 1000 * 60 * 60 * 24:
		return "{}h, {}m, {}s".format(length.hour, length.minute, length.second)
	else:
		return "{}d, {}h, {}m, {}s".format(length.day, length.hour, length.minute, length.second)


def parse_local_iso_datetime(z: str) -> datetime:
	return datetime.strptime(z, '%Y-%m-%dT%H:%M:%S.%f')



__all__ = ['mkdatetime', 'now', 'today', 'mkdate', 'this_year', 'year_range', 'format_time', 'timestamp', 'timestamp_path', 'nice_time', 'parse_local_iso_datetime']
