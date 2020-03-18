from typing import Any, Union

class Chars:
	"""Unicode symbols that are useful in code and annoying to search for repeatedly."""
	# punctuation
	nbsp = u'\u00A0'  # non-breaking space
	zwidthspace = u'\u200B'  # zero-width space
	thinspace = u'\u2009'
	hairspace = u'\u200A'
	emspace = u'\u2003'
	figspace = u'\u2007'
	narrownbsp = u'\u202F'  # great for units
	hyphen = '‐'  # proper unicode hyphen
	nbhyphen = '‑'  # non-breaking hyphen
	fig = '‒'  # figure dash, ex in phone numbers
	en = '–'  # en dash, ex in ranges
	em = '—'  # em dash, like a semicolon
	ellipsis = '…'  # only 1 character, which is helpful
	middots = '⋯'
	middot = '·'
	rsq, lsq, rdq, ldq = '’', '‘', '”', '“'
	# math
	ell = 'ℓ'
	micro, degree, angstrom = 'µ', '°', 'Å'
	minus, times, plusminus = '−', '×', '±'
	inf, null = '∞', '⌀'
	prop, approx, leq, geq = '∝', '≈', '≤', '≥'
	nott, implies, iff, forall, exists, notexists = '¬', '⇒', '⇔', '∀', '∃', '∄'
	vee, wedge, cup, cap = '∨', '∧', '∪', '∩'
	isin, contains, complement = '∈', '∋', '∁'
	precedes, succeeds = '≺', '≻'
	prime, partial, integral = '′', '∂', '∫'
	# info marks
	bullet = '•'
	dagger, ddagger = '†', '‡'
	star, snowflake = '★', '⁕'
	info, caution, warning, donotenter, noentry = '🛈', '☡', '⚠', '⛔', '🚫'
	trash, skull, atom, radiation, bioharzard = '🗑', '☠', '⚛', '☢', '☣'
	corners = '⛶'
	# misc / UI
	left, right, cycle, fatright = '←', '→', '⟳', '⮕'
	check, x = '✔', '✘'
	smile, frown, happy, worried, confused = '🙂', '☹', '😃', '😟', '😕'
	circle, square, triangle = '⚪', '◼', '▶'
	vline, hline, vdots = '|', '―', '⁞'
	bar, pipe, brokenbar, tech, zigzag = '―', '‖', '¦', '⌇', '⦚'
	# brackets
	langle, rangle = '⟨', '⟩'
	lshell, rshell = '⦗', '⦘'
	ldbracket, rdbracket = '⟦', '〛'
	ldshell, rdshell = '〘', '〙'
	ldparen, rdparen = '⸨', '⸩'
	ldangle, rdangle = '《', '》'
	# greek
	alpha, beta, gamma, delta, epsilon, eta, theta, zeta, kappa = 'α', 'β', 'γ', 'δ', 'ε', 'η', 'θ', 'ζ', 'κ'
	Gamma, Delta, Pi, Sigma, Omega = 'Γ', 'Δ',  'Π', 'Σ', 'Ω'
	lamba = 'λ'  # spelled wrong
	nu, mu, xi, tau, pi, sigma, phi, psi, omega = 'ν', 'μ', 'ξ', 'τ', 'π', 'σ', 'φ', 'ψ', 'ω'
	varphi = 'φ'

	@classmethod
	def range(cls, start: Any, end: Any) -> str:
		return str(start) + cls.en + str(end)

	@classmethod
	def squoted(cls, s: Any) -> str:
		"""Wrap a string in singsle quotes."""
		return Chars.lsq + str(s) + Chars.rsq

	@classmethod
	def dquoted(cls, s: Any) -> str:
		"""Wrap a string in double quotes."""
		return Chars.ldq + str(s) + Chars.rdq

	@classmethod
	def angled(cls, s: Any) -> str:
		"""Wrap a string in angled brackets."""
		return Chars.langle + str(s) + Chars.rangle

	@classmethod
	def dangled(cls, s: Any) -> str:
		"""Wrap a string in double brackets."""
		return Chars.ldangle + str(s) + Chars.rdangle

	@classmethod
	def parened(cls, s: Any) -> str:
		"""Wrap a string in parentheses."""
		return '(' + str(s) + ')'

	@classmethod
	def bracketed(cls, s: Any) -> str:
		"""Wrap a string in square brackets."""
		return '[' + str(s) + ']'

	@classmethod
	def braced(cls, s: Any) -> str:
		"""Wrap a string in curly braces."""
		return '{' + str(s) + '}'

	@classmethod
	def shelled(cls, s: Any) -> str:
		"""Wrap a string in tortiose shell brackets (〔 〕)."""
		return '〔' + str(s) + '〕'

	@classmethod
	def dbracketed(cls, s: Any) -> str:
		"""Wrap a string in double square brackets (⟦ ⟧)."""
		return Chars.ldbracket + str(s) + Chars.rdbracket


__all__ = ['Chars']
