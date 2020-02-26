from typing import Optional, Sequence, Union, Iterable, Tuple, Mapping, TypeVar
import re
from copy import copy
import numpy as np
from dscience_gists.tools.base_tools import BaseTools
from dscience_gists.core.chars import *
T = TypeVar('T')
V = TypeVar('V')


class StringTools(BaseTools):

	@classmethod
	def truncate(cls, s: Optional[str], n: int, always_dots: bool = False) -> Optional[str]:
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

	@classmethod
	def tabs_to_list(cls, s: str) -> Sequence[str]:
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
	@classmethod
	def truncate60(cls, s): return StringTools.truncate(s, 60)
	@classmethod
	def truncate40(cls, s): return StringTools.truncate(s, 60)
	@classmethod
	def truncate30(cls, s): return StringTools.truncate(s, 30)
	@classmethod
	def truncate10(cls, s): return StringTools.truncate(s, 10)
	@classmethod
	def truncate10_nodots(cls, s): return StringTools.truncate(s, 10, False)

	@classmethod
	def longest_str(cls, parts: Iterable[str]) -> str:
		"""
		Returns the argmax by length.
		"""
		mx = ''
		for i, x in enumerate(parts):
			if len(x) > len(mx):
				mx = x
		return mx

	@classmethod
	def strip_off_start(cls, s: str, pre: str):
		"""
		Strips the full string `pre` from the start of `str`.
		See `Tools.strip_off` for more info.
		"""
		assert isinstance(pre, str), "{} is not a string".format(pre)
		if s.startswith(pre):
			s = s[len(pre):]
		return s

	@classmethod
	def strip_off_end(cls, s: str, suf: str):
		"""
		Strips the full string `suf` from the end of `str`.
		See `Tools.strip_off` for more info.
		"""
		assert isinstance(suf, str), "{} is not a string".format(suf)
		if s.endswith(suf):
			s = s[:-len(suf)]
		return s

	@classmethod
	def strip_off(cls, s: str, prefix_or_suffix: str) -> str:
		"""
		Strip a substring from the beginning or end of a string (at most 1 occurrence).
		"""
		return StringTools.strip_off_start(StringTools.strip_off_end(s, prefix_or_suffix), prefix_or_suffix)

	@classmethod
	def strip_ends(cls, s: str, prefix: str, suffix: str) -> str:
		"""
		Strip a substring from the start, and another substring from the end, of a string (at most 1 occurrence each).
		"""
		return StringTools.strip_off_start(StringTools.strip_off_end(s, suffix), prefix)

	@classmethod
	def strip_any_ends(cls, s: str, prefixes: Union[str, Sequence[str]], suffixes: Union[str, Sequence[str]]) -> str:
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

	@classmethod
	def strip_brackets(cls, text: str) -> str:
		"""
		Strip any and all pairs of brackets from start and end of a string, but only if they're paired.
		See `strip_paired`
		"""
		pieces = [
				('(', ')'), ('[', ']'), ('[', ']'), ('{', '}'), ('<', '>'),
				(Chars.lshell, Chars.rshell), (Chars.langle, Chars.rangle),
				(Chars.ldparen, Chars.rdparen), (Chars.ldbracket, Chars.rdbracket), (Chars.ldangle, Chars.rdangle), (Chars.ldshell, Chars.rdshell)
			]
		return StringTools.strip_paired(text, pieces)

	@classmethod
	def strip_quotes(cls, text: str) -> str:
		"""
		Strip any and all pairs of quotes from start and end of a string, but only if they're paired.
		See `strip_paired`
		"""
		pieces = [
				('`', '`'),
				(Chars.lsq, Chars.rsq), (Chars.ldq, Chars.rdq), ("'", "'"), ('"', '"')
			]
		return StringTools.strip_paired(text, pieces)

	@classmethod
	def strip_brackets_and_quotes(cls, text: str) -> str:
		"""
		Strip any and all pairs of brackets and quotes from start and end of a string, but only if they're paired.
		See `strip_paired`
		"""
		pieces = [
				('(', ')'), ('[', ']'), ('[', ']'), ('{', '}'), ('<', '>'),
				(Chars.lshell, Chars.rshell), (Chars.langle, Chars.rangle),
				('`', '`'),
				(Chars.lsq, Chars.rsq), (Chars.ldq, Chars.rdq), ("'", "'"), ('"', '"'),
				(Chars.ldparen, Chars.rdparen), (Chars.ldbracket, Chars.rdbracket), (Chars.ldangle, Chars.rdangle), (Chars.ldshell, Chars.rdshell)
			]
		return StringTools.strip_paired(text, pieces)

	@classmethod
	def strip_paired(cls, text: str, pieces: Iterable[Tuple[str, str]]) -> str:
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

	@classmethod
	def replace_all(cls, s: str, rep: Mapping[str, str]) -> str:
		"""
		Simply replace multiple things in a string.
		"""
		for k, v in rep.items():
			s = s.replace(k, v)
		return s

	@classmethod
	def superscript(cls, s: Union[str, float]) -> str:
		"""
		Replaces digits, +, =, (, and ) with equivalent Unicode superscript chars (ex ¹).
		"""
		return ''.join(dict(zip("0123456789-+=()", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺⁼⁽⁾")).get(c, c) for c in StringTools.dashes_to_hm(s))

	@classmethod
	def subscript(cls, s: Union[str, float]) -> str:
		"""
		Replaces digits, +, =, (, and ) with equivalent Unicode subscript chars (ex ₁).
		"""
		return ''.join(dict(zip("0123456789+-=()", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎")).get(c, c) for c in StringTools.dashes_to_hm(s))

	@classmethod
	def unsuperscript(cls, s: Union[str, float]) -> str:
		"""
		Replaces Unicode superscript digits, +, =, (, and ) with normal chars.
		"""
		return ''.join(dict(zip("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺⁼⁽⁾", "0123456789-+=()")).get(c, c) for c in StringTools.dashes_to_hm(s))

	@classmethod
	def unsubscript(cls, s: Union[str, float]) -> str:
		"""
		Replaces Unicode superscript digits, +, =, (, and ) with normal chars.
		"""
		return ''.join(dict(zip("₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎", "0123456789+-=()")).get(c, c) for c in StringTools.dashes_to_hm(s))

	@classmethod
	def dashes_to_hm(cls, s: str) -> str:
		"""
		Replaces most Latin-alphabet dash-like and hyphen-like characters with a hyphen-minus.
		"""
		smallem = '﹘'
		smallhm = '﹣'
		fullhm = '－'
		for c in [Chars.em, Chars.en, Chars.fig, Chars.minus, Chars.hyphen, Chars.nbhyphen, smallem, smallhm, fullhm]:
			s = str(s).replace(c, '-')
		return s

	@classmethod
	def pretty_float(cls, v: Union[float, int], n_sigfigs: Optional[int] = 5) -> str:
		"""
		Represents a float as a string, with symbols for NaN and infinity.
		The returned string always has a minus or + prepended. Strip off the plus with .lstrip('+').
		If v is an integer (by isinstance), makes sure to display without a decimal point.
		If n_sigfigs < 2, will never have a
		For ex:
			- StringTools.pretty_float(.2222222)       # '+0.22222'
			- StringTools.pretty_float(-.2222222)      # '−0.22222' (Unicode minus)
			- StringTools.pretty_float(-float('inf'))  # '−∞'
			- StringTools.pretty_float(np.NaN)         # '⌀'
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

	@classmethod
	def pretty_function(cls, function, with_address: bool = False, prefix: str = '⟨', suffix: str = '⟩') -> str:
		"""
		Get a better and shorter name for a function than str(function).
		Ex: pprint_function(lambda s: s)  == '<λ>'
		- Instead of '<bound method ...', you'll get '<name(nargs)>'
		- Instead of 'lambda ...', you'll get '<λ(nargs)>'
		- etc.
		NOTE 1: If function is None, returns ''
		NOTE 2: If function does not have __name__, returns prefix + type(function) + <address> + suffix
		:param function: Can be anything, but especially useful for functions
		:param with_address: Include `@ hex-mem-addr` in the name
		:param prefix: Prefix to the whole string
		:param suffix: Suffix to the whole string
		"""
		if function is None:
			return ''
		n_args = str(function.__code__.co_argcount) if hasattr(function, '__code__') else '?'
		boundmatch = re.compile(r'^<bound method [^ .]+\.([^ ]+) of (.+)>$').fullmatch(str(function))
		objmatch = re.compile(r'<([A-Za-z0-9_.]+) object').search(str(function))
		addr = ' @ ' + hex(id(function)) if with_address else ''
		if cls.is_lambda(function):
			# simplify lambda functions!
			return prefix + 'λ(' + n_args + ')' + addr + suffix
		elif boundmatch is not None:
			# it's a method (bound function)
			# don't show the address of the instance AND its method
			s = re.compile(r'@ ?0x[0-9a-hA-H]+\)?$').sub('', boundmatch.group(2)).strip()
			return prefix + '`' + s + '`.' + boundmatch.group(1) + '(' + n_args + ')' + addr + suffix
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

	@classmethod
	def greek_to_name(cls) -> Mapping[str, str]:
		"""
		Returns a dict from Greek lowercase+uppercase Unicode chars to their full names
		@return A defensive copy
		"""
		return copy(StringTools._greek_alphabet)

	@classmethod
	def name_to_greek(cls) -> Mapping[str, str]:
		"""
		Returns a dict from Greek lowercase+uppercase letter names to their Unicode chars
		@return A defensive copy
		"""
		return {v: k for k, v in StringTools._greek_alphabet.items()}

	@classmethod
	def fix_greek(cls, s: str, lowercase: bool = False) -> str:
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

	@classmethod
	def join(cls, seq: Iterable[T], sep: str = '\t', attr: Optional[str] = None, prefix: str = '', suffix: str = '') -> str:
		"""
		Join elements into a str more easily than ''.join. Just simplifies potentially long expressions.
		Won't break with ValueError if the elements aren't strs.
		Ex:
			- StringTools.join([1,2,3])  # "1	2	3"
			- StringTools.join(cars, sep=',', attr='make', prefix="(", suffix=")")`  # "(Ford),(Ford),(BMW)"

		:param seq: Sequence of elements
		:param sep: Delimiter
		:param attr: Get this attribute from each element (in `seq`), or use the element itself if None
		:param prefix: Prefix before each item
		:param suffix: Suffix after each item
		:return: A string
		"""
		if attr is None:
			return sep.join([prefix + str(s) + suffix for s in seq])
		else:
			return sep.join([prefix + str(getattr(s, attr)) + suffix for s in seq])

	@classmethod
	def join_kv(cls, seq: Mapping[T, V], sep: str = '\t', eq: str = '=', prefix: str = '', suffix: str = '') -> str:
		"""
		Joins dict elements into a str like 'a=1, b=2, c=3`.
		Won't break with ValueError if the keys or values aren't strs.
		:param seq: Dict-like, with `items()`
		:param sep: Delimiter
		:param eq: Separates a key with its value
		:param prefix: Prepend before every key
		:param suffix: Append after every value
		:return: A string
		"""
		return sep.join([prefix + str(k) + eq + str(v) + suffix for k, v in seq.items()])

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
		u'\u039B': 'Lambda',
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
		u'\u03BB': 'lambda',
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


__all__ = ['StringTools']
