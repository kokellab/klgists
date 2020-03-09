from typing import SupportsFloat, Optional, Tuple, Union
import re
import logging
import math
import humanfriendly as friendly
from dscience.core.exceptions import OutOfRangeError, StringPatternError
from dscience.tools.base_tools import BaseTools
from dscience.tools.string_tools import StringTools
logger = logging.getLogger('dscience')


class UnitTools(BaseTools):

	@classmethod
	def delta_time_to_str(cls, delta_sec: float, space: str = '') -> str:
		"""
		Returns a pretty string from a difference in time in seconds. Rounds hours and minutes to 2 decimal places, and seconds to 1.
		Ex: delta_time_to_str(313) == 5.22min
		:param delta_sec: The time in seconds
		:param space: Space char between digits and units; good choices are empty, ASCII space, Chars.narrownbsp, Chars.thinspace, and Chars.nbsp.
		:return: A string with units 'hr', 'min', or 's'
		"""
		if abs(delta_sec) > 60*60*3:
			return StringTools.strip_empty_decimal(str(round(delta_sec/60/60, 2))) + space + 'hr'
		elif abs(delta_sec) > 180:
			return StringTools.strip_empty_decimal(str(round(delta_sec/60, 2))) + space + 'min'
		else:
			return StringTools.strip_empty_decimal(str(round(delta_sec, 1))) + space + 's'

	@classmethod
	def ms_to_minsec(cls, ms: int, space: str = '') -> str:
		"""
		Converts a number of milliseconds to one of the following formats:
			- 10ms         if < 1 sec
			- 10:15        if < 1 hour
			- 10:15:33     if < 1 day
			- 5d:10:15:33  if > 1 day
		Prepends a minus sign (−) if negative.
		:param ms: The milliseconds
		:param space: Space char between digits and 'ms' or 'd' for day (if used); good choices are empty, ASCII space, Chars.narrownbsp, Chars.thinspace, and Chars.nbsp.
		:return: A string of one of the formats above
		"""
		is_neg = ms < 0
		ms = abs(int(ms))
		seconds = int((ms/1000) % 60)
		minutes = int((ms/(1000*60)) % 60)
		hours = int((ms/(1000*60*60)) % 24)
		days = int(ms/(1000*60*60*24))
		if ms < 1000:
			s = "{}{}ms".format(space, ms)
		elif days > 1:
			s = "{}{}d:{}:{}:{}".format(days, space, str(hours).zfill(2), str(minutes).zfill(2), str(seconds).zfill(2))
		elif hours > 1:
			s = "{}:{}:{}".format(str(hours).zfill(2), str(minutes).zfill(2), str(seconds).zfill(2))
		else:
			s = "{}:{}".format(str(minutes).zfill(2), str(seconds).zfill(2))
		return '−' + s if is_neg else s

	@classmethod
	def friendly_size(cls, n_bytes: int) -> str:
		"""
		Returns a text representation of a number of bytes.
		Uses base 2 with units 'b', 'kb', 'mb', etc., rounded to 0 decimal places, and without a space.
		"""
		n, u = friendly.format_size(n_bytes, binary=True).split(' ')
		return str(round(float(n))) + u.replace('bytes', 'b').replace('i', '').lower()

	@classmethod
	def round_to_sigfigs(cls, num: SupportsFloat, sig_figs: int) -> int:
		"""
		Round to specified number of sigfigs.
		:param num: A Python or Numpy float or something that supports __float__
		:param sig_figs: The number of significant figures, non-negative
		:return: A Python integer
		"""
		if sig_figs < 0:
			raise OutOfRangeError("sig_figs {} is negative".format(sig_figs), minimum=0)
		num = float(num)
		if num != 0:
			return round(num, -int(math.floor(math.log10(abs(num))) - (sig_figs - 1)))
		else:
			return 0  # can't take the log of 0

	@classmethod
	def nice_dose(cls, micromolar_dose: float, n_sigfigs: Optional[int] = 5, adjust_units: bool = True, use_sigfigs: bool = True, space: str = '') -> str:
		"""
		Returns a dose with units, with the units scaled as needed.
		Can handle millimolar, micromolar, nanomolar, and picomolar.
		:param use_sigfigs: If True, rounds to a number of significant figures; otherwise round to decimal places
		:param micromolar_dose: The dose in micromolar
		:param n_sigfigs: For rounding; no rounding if None
		:param adjust_units: If False, will always use micromolar
		:param space: Space char between digits and units; good choices are empty, ASCII space, Chars.narrownbsp, Chars.thinspace, and Chars.nbsp.
		:return: The dose with a suffix of µM, mM, nM, or mM
		"""
		d = micromolar_dose
		m = abs(d)
		unit = 'µM'
		if adjust_units:
			if m < 1E-6:
				d *= 1E9
				unit = 'fM'
			elif m < 1E-3:
				d *= 1E6
				unit = 'pM'
			elif m < 1:
				d *= 1E3
				unit = 'nM'
			elif m >= 1E6:
				d /= 1E6
				unit = 'M'
			elif m >= 1E3:
				d /= 1E3
				unit = 'mM'
		if n_sigfigs is None:
			pass
		elif use_sigfigs:
			d = UnitTools.round_to_sigfigs(d, n_sigfigs)
		else:
			d = round(d, n_sigfigs)
		if round(d) == d and str(d).endswith('.0'):
			return str(d)[:-2] + space + unit
		else: return str(d) + space + unit

	@classmethod
	def split_drug_dose(cls, text: str) -> Tuple[str, Optional[float]]:
		"""
		Splits a name into a drug/dose pair, falling back with the full name.
		Ex: "abc 3.5uM" → (abc, 3.5)
		Ex: "abc 3.5 µM" → (abc, 3.5)
		Ex: "abc (3.5mM)" → (abc, 3500.0)
		Ex: "abc 3.5mM" → (abc, None)
		Ex: "3.5mM" → (3.5mM, None)  # an edge case: don't pass in only units
		Uses a moderately strict pattern for the drug and dose:
			- The dose must terminate the string, except for end parenthesis or whitespace.
			- The drug and dose must be separated by at least one non-alphanumeric, non-dot, non-hyphen character.
			- Units must follow the digits, separated by at most whitespace, and are case-sensitive.
		"""
		# note the lazy ops in the first group and in the non-(alphanumeric/dot/dash) separator between the drug and dose
		pat = re.compile(r'^\s*(.*?)(?:[^A-Za-z0-9.\-]+?[\s(\[{]*(\d+(?:.\d*)?)\s*([mµunpf]M)\s*[)\]}]*)?\s*$')
		match = pat.fullmatch(text)
		if match is None:
			raise StringPatternError("The text {} couldn't be parsed".format(text), value=text, pattern=pat)
		if match.group(2) is None:
			return text.strip(), None
		else:
			drug = match.group(1).strip('([{)]}')
			dose = UnitTools.dose_to_micromolar(float(match.group(2)), match.group(3))
			return drug, dose

	@classmethod
	def extract_dose(cls, text: str) -> Optional[float]:
		"""
		Returns what looks like a concentration with units. Accepts one of: mM, µM, uM, nM, pM.
		Searches pretty flexibly.
		If no matches are found, returns None.
		If multiple matches are found, warns and returns None.
		"""
		# we need to make sure mM ex isn't part of a larger name
		pat1 = re.compile(r'(\d+(?:.\d*)?)\s*([mµunpf]M)\s*[)\]}]*')
		def find(pat):
			return {
				UnitTools.dose_to_micromolar(float(match.group(1)), match.group(2))
				for match in pat.finditer(text)
				if match is not None
			}
		matches = find(pat1)
		if len(matches) == 1:
			return next(iter(matches))
		elif len(matches) > 1:
			logger.warning("Found {} potential doses: {} . Returning None.".format(len(matches), matches))
		return None

	@classmethod
	def dose_to_micromolar(cls, digits: Union[str, float], units: str) -> float:
		"""
		Ex: dose_to_micromolar(53, 'nM')  # returns 0.053
		"""
		return float(digits) *{
			'M':  1e6,
			'mM': 1e3,
			'µM': 1,
			'uM': 1,
			'nM': 1e-3,
			'pM': 1e-6,
			'fM': 1e-9
		}[units]


__all__ = ['UnitTools']
