from typing import Dict
from typing import SupportsFloat, SupportsInt
from klgists.common.tools import *
from klgists.common import *
from klgists.common.chars import *
from klgists.pandas.extended_df import TrivialExtendedDataFrame, ConvertibleExtendedDataFrame, FinalExtendedDataFrame
from klgists.common.exceptions import UserError
from pathlib import Path, PurePath
from copy import copy


import os
import numpy as np
import pandas as pd

PLike = Union[str, PurePath, os.PathLike]
V = TypeVar('V')


class NumericTools(VeryCommonTools):

	@staticmethod
	def fnone(f: Optional[SupportsFloat]) -> float:
		return None if f is None else float(f)

	@staticmethod
	def iroundopt(f: Optional[SupportsInt]) -> int:
		# noinspection PyTypeChecker
		return None if f is None else int(np.round(f))

	@staticmethod
	def iceilopt(f: Optional[SupportsInt]) -> int:
		# noinspection PyTypeChecker
		return None if f is None else int(np.ceil(f))

	@staticmethod
	def iflooropt(f: Optional[SupportsInt]) -> int:
		# noinspection PyTypeChecker
		return None if f is None else int(np.floor(f))

	@staticmethod
	def iround(f: Optional[SupportsInt]) -> int:
		# noinspection PyTypeChecker
		return None if f is None else int(np.round(f))

	@staticmethod
	def iceil(f: SupportsFloat) -> int:
		"""
		Fixes np.ceil to return an Python integer rather than a Numpy float.
		:param f: A Python or Numpy float, or something else that defines __float__
		:return: An integer of the ceiling
		"""
		# noinspection PyTypeChecker
		return int(np.ceil(f))

	@staticmethod
	def ifloor(f: SupportsFloat) -> int:
		"""
		Fixes np.floor to return an Python integer rather than a Numpy float.
		:param f: A Python or Numpy float, or something else that defines __float__
		:return: An integer of the ceiling
		"""
		# noinspection PyTypeChecker
		return int(np.floor(f))

	@staticmethod
	def imin(*f):
		return int(np.min(f))

	@staticmethod
	def imax(*f):
		return int(np.max(f))

	@staticmethod
	def slice_bounded(arr: np.array, i: int, j: int) -> np.array:
		if i < 0: i = len(arr) - i
		if j < 0: j = len(arr) - j
		start, stop = NumericTools.imax(0, i), NumericTools.imin(len(arr), j)
		return arr[start : stop]


class PandasTools(VeryCommonTools):

	@staticmethod
	def df_to_dict(d: pd.DataFrame) -> Dict[Any, Any]:
		if len(d.columns) != 2:
			raise ValueError("Need exactly 2 columns (key, value); got {}".format(len(d.columns)))
		keys, values = d.columns[0], d.columns[1]
		return {
			getattr(r, keys): getattr(r, values)
			for r in d.itertuples()
		}

	@staticmethod
	def csv_to_dict(path: PLike) -> Dict[Any, Any]:
		d = pd.read_csv(Path(path))
		return PandasTools.df_to_dict(d)

	@staticmethod
	def dict_to_df(dct: Mapping[Any, Any], keys: str = 'name', values: str = 'value') -> pd.DataFrame:
		dct = dict(dct)
		return pd.DataFrame.from_dict(dct, orient='index').reset_index().rename(columns={'index': keys, 0: values})

	@staticmethod
	def dict_to_csv(dct: Mapping[Any, Any], path: PLike, keys: str = 'name', values: str = 'value') -> None:
		PandasTools.dict_to_df(dct, keys, values).to_csv(Path(path))

	@staticmethod
	def extended_df(df: pd.DataFrame, class_name: Optional[str] = None) -> ConvertibleExtendedDataFrame:
		"""
		Wrap `df` in an extended dataframe (ConvertibleExtendedDataFrame, which is its superclass).
		The returned Pandas DataFrame will have additional methods and better display in Jupyter.
		- If `df` is already a `ConvertibleExtendedDataFrame`, will just return it.
		- Otherwise:
			* Creates a new class with name `class_name` if `class_name` is non-null.
			* Otherwise wraps in a `FinalExtendedDataFrame`.
		:param df: Any Pandas DataFrame.
		:param class_name: Only applies if `df` isn't already a `ConvertibleExtendedDataFrame`
		:return: A copy of `df` of the new class
		"""
		if isinstance(df, ConvertibleExtendedDataFrame):
			return df
		elif isinstance(df, pd.DataFrame):
			if class_name is None:
				return FinalExtendedDataFrame(df)
			else:
				class X(TrivialExtendedDataFrame): pass
				X.__name__ = class_name
				return X(df)
		else:
			raise UserError("Invalid DataFrame type {}".format(df))

	@staticmethod
	def series_to_df(series, column: str) -> pd.DataFrame:
		return TrivialExtendedDataFrame(series).reset_index().rename(columns={0: column})


class StringTools(VeryCommonTools):

	@staticmethod
	def truncate(s: Optional[str], n: int, always_dots: bool = False) -> Optional[str]:
		"""
		Returns a string if it has `n` or fewer characters; otherwise truncates to length `n-1` and appends `…` (UTF character).
		If `s` is None and `always_dots` is True, returns `n` copies of `.` (as a string).
		If `s` is None otherwise, returns None.
		:param s: The string
		:param n: The maximum length, inclusive
		:param always_dots: Use dots instead of returning None; see above
		:return: A string or None
		"""
		if s is None and always_dots:
			return '…' * n
		if s is None:
			return None
		if len(s) > n:
			nx = max(0, n - 1)
			return s[:nx] + '…'
		return s

	@staticmethod
	def tabs_to_list(s: str) -> Sequence[str]:
		"""
		Splits by tabs, but preserving quoted tabs, stripping quotes.
		"""
		pat = re.compile(r'''((?:[^\t"']|"[^"]*"|'[^']*')+)''')

		# Don't strip double 2x quotes: ex ""55"" should be "55", not 55
		def strip(i: str) -> str:
			if i.endswith('"') or i.endswith("'"):
				i = i[:-1]
			if i.startswith('"') or i.startswith("'"):
				i = i[1:]
			return i.strip()

		return [strip(i) for i in pat.findall(s)]

	# these are provided to avoid having to call with labdas or functools.partial
	@staticmethod
	def truncate60(s): return StringTools.truncate(s, 60)
	@staticmethod
	def truncate40(s): return StringTools.truncate(s, 60)
	@staticmethod
	def truncate30(s): return StringTools.truncate(s, 30)
	@staticmethod
	def truncate10(s): return StringTools.truncate(s, 10)
	@staticmethod
	def truncate10_nodots(s): return StringTools.truncate(s, 10, False)

	@staticmethod
	def longest_str(parts: Iterable[str]) -> str:
		mx = ''
		for i, x in enumerate(parts):
			if len(x) > len(mx):
				mx = x
		return mx

	@staticmethod
	def strip_off_start(s: str, pre: str):
		return strip_off_start(s, pre)

	@staticmethod
	def strip_off_end(s: str, pre: str):
		return strip_off_end(s, pre)

	@staticmethod
	def strip_off(s: str, prefix_or_suffix: str) -> str:
		return strip_off_start(strip_off_end(s, prefix_or_suffix), prefix_or_suffix)

	@staticmethod
	def strip_ends(s: str, prefix: str, suffix: str) -> str:
		return strip_off_start(strip_off_end(s, suffix), prefix)

	@staticmethod
	def strip_any_ends(s: str, prefixes: Union[str, Sequence[str]], suffixes: Union[str, Sequence[str]]) -> str:
		"""
		Flexible variant that strips any number of prefixes and any number of suffixes.
		Also less type-safe than more specific variants.
		Note that the order of the prefixes (or suffixes) DOES matter.
		"""
		prefixes = [str(z) for z in prefixes] if StringTools.is_true_iterable(prefixes) else [str(prefixes)]
		suffixes = [str(z) for z in suffixes] if StringTools.is_true_iterable(suffixes) else [str(suffixes)]
		s = str(s)
		for pre in prefixes:
			if s.startswith(pre):
				s = s[len(pre):]
		for suf in suffixes:
			if s.endswith(suf):
				s = s[:-len(suf)]
		return s

	@staticmethod
	def strip_brackets(text: str) -> str:
		"""
		Strip any and all pairs of brackets from start and end of a string, but only if they're paired.
		See `strip_paired`
		"""
		pieces =  [
				('(', ')'), ('[', ']'), ('[', ']'), ('{', '}'), ('<', '>'),
				(Chars.lshell, Chars.rshell), (Chars.langle, Chars.rangle),
				(Chars.ldparen, Chars.rdparen), (Chars.ldbracket, Chars.rdbracket), (Chars.ldangle, Chars.rdangle), (Chars.ldshell, Chars.rdshell)
			]
		return StringTools.strip_paired(text, pieces)

	@staticmethod
	def strip_quotes(text: str) -> str:
		"""
		Strip any and all pairs of quotes from start and end of a string, but only if they're paired.
		See `strip_paired`
		"""
		pieces =  [
				('`', '`'),
				(Chars.lsq, Chars.rsq), (Chars.ldq, Chars.rdq), ("'", "'"), ('"', '"')
			]
		return StringTools.strip_paired(text, pieces)

	@staticmethod
	def strip_brackets_and_quotes(text: str) -> str:
		"""
		Strip any and all pairs of brackets and quotes from start and end of a string, but only if they're paired.
		See `strip_paired`
		"""
		pieces =  [
				('(', ')'), ('[', ']'), ('[', ']'), ('{', '}'), ('<', '>'),
				(Chars.lshell, Chars.rshell), (Chars.langle, Chars.rangle),
				('`', '`'),
				(Chars.lsq, Chars.rsq), (Chars.ldq, Chars.rdq), ("'", "'"), ('"', '"'),
				(Chars.ldparen, Chars.rdparen), (Chars.ldbracket, Chars.rdbracket), (Chars.ldangle, Chars.rdangle), (Chars.ldshell, Chars.rdshell)
			]
		return StringTools.strip_paired(text, pieces)

	@staticmethod
	def strip_paired(text: str, pieces: Iterable[Tuple[str, str]]) -> str:
		"""
		Strip pairs of (start, end) from the ends of strings. For example:
		```
		Tools.strip_paired('[(abc]', ['()', '[]'])  # returns '(abc'
		Also see `strip_brackets`
		```
		"""
		if any([a for a in pieces if len(a) != 2]):
			raise ValueError("strip_paired requires each item in `pieces` be a string of length 2: (stard, end); got {}".format(pieces))
		text = str(text)
		while len(text) > 1:
			for _ in [0 for a, b in pieces if text.startswith(a) and text.endswith(b)]:
				text = text[1:-1]
			else:
				break
		return text

	@staticmethod
	def replace_all(s: str, rep: Mapping[str, str]) -> str:
		for k, v in rep.items():
			s = s.replace(k, v)
		return s

	@staticmethod
	def superscript(s: Union[str, float]) -> str:
		return ''.join(dict(zip("0123456789i-+=()n", "⁰¹²³⁴⁵⁶⁷⁸⁹ⁱ⁻⁺⁼⁽⁾ⁿ")).get(c, c) for c in StringTools.dashes_to_hm(s))

	@staticmethod
	def subscript(s: Union[str, float]) -> str:
		return ''.join(dict(zip("0123456789+-=()aeoxhklmnpstj", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₒₓₕₖₗₘₙₚₛₜⱼ")).get(c, c) for c in StringTools.dashes_to_hm(s))

	@staticmethod
	def unsuperscript(s: Union[str, float]) -> str:
		return ''.join(dict(zip("⁰¹²³⁴⁵⁶⁷⁸⁹ⁱ⁻⁺⁼⁽⁾ⁿ", "0123456789i-+=()n")).get(c, c) for c in StringTools.dashes_to_hm(s))

	@staticmethod
	def unsubscript(s: Union[str, float]) -> str:
		return ''.join(dict(zip("₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₒₓₕₖₗₘₙₚₛₜⱼ", "0123456789+-=()aeoxhklmnpstj")).get(c, c) for c in StringTools.dashes_to_hm(s))

	@staticmethod
	def dashes_to_hm(s: str) -> str:
		"""Replaces most dash-like characters with a hyphen-minus."""
		return str(s).replace(Chars.em, '-').replace(Chars.en, '-').replace(Chars.fig, '-').replace(Chars.minus, '-').replace(Chars.hyphen, '-').replace(Chars.nbhyphen, '-')

	@staticmethod
	def pretty_float(v: Union[float, int], n_sigfigs: Optional[int] = 5) -> str:
		"""
		Represents a float as a string, with symbols for NaN and infinity.
		The returned string always has a minus or + prepended. Strip off the plus with .lstrip('+').
		If v is an integer (by isinstance), makes sure to display without a decimal point.
		If n_sigfigs < 2, will never have a
		"""
		v0 = v.__class__(v)
		# first, handle NaN and infinities
		if np.isneginf(v):
			return Chars.minus + Chars.inf
		elif np.isposinf(v):
			return '+' + Chars.inf
		elif np.isnan(v):
			return Chars.null
		# sweet. it's a regular float or int.
		isint = isinstance(v, int)
		if isint:
			v = int(round(v))
		if n_sigfigs is None:
			s = StringTools.strip_empty_decimal(str(v))
		else:
			s = str(float(str(('%.{}g'.format(n_sigfigs)) % v)))
		# remove the .0 if the precision doesn't support it
		# if v >= 1 and n_sigfigs<2, it couldn't have a decimal
		# and if n_sigfigs<1, it definitely can't
		if isint or n_sigfigs is not None and v0>=1 and n_sigfigs<2 or n_sigfigs is not None and n_sigfigs < 1:
			s = StringTools.strip_empty_decimal(s)
		# and ... %g does this.
		if s.startswith('.'):
			s = '0' + s
		# prepend + or -
		if s.startswith('-'):
			return Chars.minus + s[1:]
		else:
			return '+' + s

	@staticmethod
	def pretty_function(function, with_address: bool = False, prefix: str = '⟨', suffix: str = '⟩') -> str:
		"""
		Get a shorter name for a function than str(function).
		Ex: pprint_function(lambda s: s)  == '<λ>'
		NOTE: If function is None, returns ''
		AND: If function does not have __name__, returns prefix + type(function) + <address> + suffix
		"""

		if function is None:
			return ''
		n_args = str(function.__code__.co_argcount) if hasattr(function, '__code__') else '?'
		boundmatch = re.compile(r'^<bound method [^ .]+\.([^ ]+) of (.+)>$').fullmatch(str(function))
		objmatch = re.compile(r'<([A-Za-z0-9_.]+) object').search(str(function))
		addr = ' @ ' + hex(id(function)) if with_address else ''
		if CommonTools.is_lambda(function):
			# simplify lambda functions!
			return prefix + 'λ(' + n_args + ')' + addr + suffix
		elif boundmatch is not None:
			# it's a method (bound function)
			# don't show the address of the instance AND its method
			s = re.compile(r'@ ?0x[0-9a-hA-H]+\)?$').sub('', boundmatch.group(2)).strip()
			return prefix + '`' + s + '`.' +  boundmatch.group(1) + '(' + n_args + ')' + addr + suffix
		elif isinstance(function, type):
			# it's a class
			return prefix + 'type:' + function.__name__ + suffix
		elif callable(function):
			# it's an actual function
			return prefix + function.__name__ + addr + suffix
		elif hasattr(function, '__dict__') and len(function.__dict__) > 0:
			# it's a member with attributes
			# it's interesting enough that it may have a good __str__
			s = StringTools.strip_off_end(StringTools.strip_off_start(str(function), prefix), suffix)
			return prefix + s + addr + suffix
		elif objmatch is not None:
			# it's an instance without attributes
			s = objmatch.group(1)
			if '.' in s:
				s = s[s.rindex('.')+1:]
			return prefix + s + addr + suffix
		else:
			# it's a primitive, etc
			s = StringTools.strip_off_end(StringTools.strip_off_start(str(function), prefix), suffix)
			return prefix + s + suffix

	_greek_alphabet = {
		u'\u0391': 'Alpha',
		u'\u0392': 'Beta',
		u'\u0393': 'Gamma',
		u'\u0394': 'Delta',
		u'\u0395': 'Epsilon',
		u'\u0396': 'Zeta',
		u'\u0397': 'Eta',
		u'\u0398': 'Theta',
		u'\u0399': 'Iota',
		u'\u039A': 'Kappa',
		u'\u039B': 'Lamda',
		u'\u039C': 'Mu',
		u'\u039D': 'Nu',
		u'\u039E': 'Xi',
		u'\u039F': 'Omicron',
		u'\u03A0': 'Pi',
		u'\u03A1': 'Rho',
		u'\u03A3': 'Sigma',
		u'\u03A4': 'Tau',
		u'\u03A5': 'Upsilon',
		u'\u03A6': 'Phi',
		u'\u03A7': 'Chi',
		u'\u03A8': 'Psi',
		u'\u03A9': 'Omega',
		u'\u03B1': 'alpha',
		u'\u03B2': 'beta',
		u'\u03B3': 'gamma',
		u'\u03B4': 'delta',
		u'\u03B5': 'epsilon',
		u'\u03B6': 'zeta',
		u'\u03B7': 'eta',
		u'\u03B8': 'theta',
		u'\u03B9': 'iota',
		u'\u03BA': 'kappa',
		u'\u03BB': 'lamda',
		u'\u03BC': 'mu',
		u'\u03BD': 'nu',
		u'\u03BE': 'xi',
		u'\u03BF': 'omicron',
		u'\u03C0': 'pi',
		u'\u03C1': 'rho',
		u'\u03C3': 'sigma',
		u'\u03C4': 'tau',
		u'\u03C5': 'upsilon',
		u'\u03C6': 'phi',
		u'\u03C7': 'chi',
		u'\u03C8': 'psi',
		u'\u03C9': 'omega',
	}

	@staticmethod
	def greek_to_name():
		return copy(StringTools._greek_alphabet)

	@staticmethod
	def name_to_greek():
		return {v: k for k, v in StringTools._greek_alphabet.items()}

	@staticmethod
	def fix_greek(s: str, lowercase: bool = False) -> str:
		"""
		Replaces Greek letter names with their Unicode equivalents.
		Does this correctly by replacing superstrings before substrings.
		Ex: '1-beta' is '1-β' rather than '1-bη'
		If lowercase is True: Replaces Beta, BeTa, and BETA with β
		Else: Replaces Beta with a capital Greek Beta and ignores BETA and BeTa.
		"""
		# Clever if I may say so:
		# If we just sort from longest to shortest, we can't replace substrings by accident
		# For example we'll replace 'beta' before 'eta', so '1-beta' won't become '1-bη'
		greek = sorted([(v, k) for k, v in StringTools._greek_alphabet.items()], key=lambda t: -len(t[1]))
		for k, v in greek:
			if k[0].isupper() and lowercase: continue
			if lowercase:
				s = re.compile(k, re.IGNORECASE).sub(v, s)
			else:
				s = s.replace(k, v)
		return s

	@staticmethod
	def join(seq: Iterable[T], sep: str = '\t', attr: Optional[str] = None, prefix: str = '', suffix: str = '') -> str:
		if attr is None:
			return sep.join([prefix + str(s) + suffix for s in seq])
		else:
			return sep.join([prefix + str(getattr(s, attr)) + suffix for s in seq])

	@staticmethod
	def join_kv(seq: Mapping[T, V], sep: str = '\t') -> str:
		return sep.join([str(k) + '=' + str(v) for k, v in seq.items()])


__all__ = ['NumericTools', 'PandasTools', 'StringTools']