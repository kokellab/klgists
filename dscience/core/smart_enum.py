from __future__ import annotations
import enum


class SmartEnum(enum.Enum):
	"""
	An enum with a classmethod `of` that parses a string of the member's name.
	"""
	@classmethod
	def of(cls, v):
		"""
		Returns the member of this enum class from a string with the member's name, case-insentive and stripping whitespace.
		Will return `v` if `v` is already an instance of this class.
		"""
		if isinstance(v, cls):
			return v
		elif isinstance(v, str):
			if v in cls:
				return cls[v.upper().strip()]
			else:
				# in case the names are lowercase
				# noinspection PyTypeChecker
				for e in cls:
					if e.name.lower().strip() == v:
						return e
				raise LookupError("{} not found in {}".format(v, str(cls)))
		else:
			raise TypeError(str(type(v)))

__all__ = ['SmartEnum']