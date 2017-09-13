from datetime import date, datetime, time, timedelta, timezone, tzinfo
import datetime as dt
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
