from klgists.common.tools import *
from typing import SupportsFloat

import humanfriendly as friendly
import math


class UnitTools:

	@staticmethod
	def friendly_size(n_bytes: int) -> str:
		"""
		Returns a text representation of a number of bytes.
		Uses base 2 with units 'b', 'kb', 'mb', etc., rounded to 0 decimal places, and without a space.
		"""
		n, u = friendly.format_size(n_bytes, binary=True).split(' ')
		return str(round(float(n))) + u.replace('bytes', 'b').replace('i', '').lower()

	@staticmethod
	def round_to_sigfigs(num: SupportsFloat, sig_figs: int) -> int:
		"""
		Round to specified number of sigfigs.
		:param num: A Python or Numpy float or something that supports __float__
		:param sig_figs: The number of significant figures, non-negative
		:return: A Python integer
		"""
		if sig_figs < 0:
			raise ValueError("sig_figs {} is negative".format(sig_figs))
		num = float(num)
		if num != 0:
			return round(num, -int(math.floor(math.log10(abs(num))) - (sig_figs - 1)))
		else:
			return 0  # can't take the log of 0

	@staticmethod
	def nice_dose(micromolar_dose: float, n_sigfigs: Optional[int] = 5, adjust_units: bool = True, use_sigfigs: bool = True) -> str:
		"""
		Returns a dose with units, with the units scaled as needed.
		Can handle millimolar, micromolar, nanomolar, and picomolar.
		:param use_sigfigs: If True, rounds to a number of significant figures; otherwise round to decimal places
		:param micromolar_dose: The dose in micromolar
		:param n_sigfigs: For rounding; no rounding if None
		:param adjust_units: If False, will always use micromolar
		:return: The dose with a suffix of µM, mM, nM, or mM
		"""
		d = micromolar_dose
		m = abs(d)
		unit = 'µM'
		if adjust_units:
			if m < 1E-6:
				d *= 1E9
				unit = 'fM'
			if m < 1E-3:
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
		if round(d) == d:
			return str(d).replace('.0', '') + unit
		else: return str(d) + unit

	@staticmethod
	def split_drug_dose(text: str) -> Tuple[str, Optional[float]]:
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
		pat = re.compile(r'^\s*(.*?)(?:[^A-Za-z0-9.\-]+?[\s(\[{]*(\d+(?:.\d*)?)\s*([mµunp]M)\s*[)\]}]*)?\s*$')
		match = pat.fullmatch(text)
		if match is None:
			raise ValueError("The text {} couldn't be parsed".format(text))
		if match.group(2) is None:
			return text.strip(), None
		else:
			drug = match.group(1).strip('([{)]}')
			dose = UnitTools.dose_to_micromolar(float(match.group(2)), match.group(3))
			return drug, dose

	@staticmethod
	def extract_dose(text: str) -> Optional[float]:
		"""
		Returns what looks like a concentration with units. Accepts one of: mM, µM, uM, nM, pM.
		Searches pretty flexibly.
		If no matches are found, returns None.
		If multiple matches are found, warns and returns None.
		"""
		# we need to make sure mM ex isn't part of a larger name
		pat1 = re.compile(r'[^A-Za-z0-9.\-](\d+(?:.\d*))[\s(\[{]*([mµunp]M)[^A-Za-z0-9]')
		pat2 = re.compile(r'^(\d+(?:\.\d*)?)[\s(\[{]*([mµunp]M)$')
		def find(pat):
			return {
				UnitTools.dose_to_micromolar(float(match.group(1)), match.group(2))
				for match in pat.finditer(text)
				if match is not None
			}
		matches = find(pat1)
		matches.update(find(pat2))
		if len(matches) == 1:
			return next(iter(matches))
		elif len(matches) > 1:
			logger.warning("Found {} potential doses: {}".format(len(matches), matches))
		return None

	@staticmethod
	def dose_to_micromolar(digits: float, units: str) -> float:
		"""
		Ex: dose_to_micromolar(53, 'nM')  # returns 0.053
		"""
		return float(digits) *{
			'mM': 1000,
			'µM': 1.0,
			'uM': 1.0,
			'nM': 1/1000,
			'pM': 1/1000
		}[units]


__all__ = ['UnitTools']