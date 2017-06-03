# coding=utf-8

import datetime

def format_time(time: datetime.datetime) -> str:
	"""Standard timestamp format. Ex: 2016-05-02_22_35_56."""
	return time.strftime("%Y-%m-%d_%H-%M-%S")

def timestamp() -> str:
	"""Standard timestamp of time now. Ex: 2016-05-02_22_35_56."""
	return format_time(datetime.datetime.now())

def timestamp_path(path: str) -> str:
	"""Standard way to label a file path with a timestamp."""
	return "{}-{}".format(path, timestamp())


def nice_time(n_ms: int) -> str:
	length = datetime.datetime(1, 1, 1) + datetime.timedelta(milliseconds=n_ms)
	if n_ms < 1000 * 60 * 60 * 24:
		return "{}h, {}m, {}s".format(length.hour, length.minute, length.second)
	else:
		return "{}d, {}h, {}m, {}s".format(length.day, length.hour, length.minute, length.second)


def parse_local_iso_datetime(z: str) -> datetime.datetime:
	return datetime.datetime.strptime(z, '%Y-%m-%dT%H:%M:%S.%f')
