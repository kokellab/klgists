"""
The motivation here is simply that Python lacks some standard exceptions that I consider important.
Projects can/should subclass from these in addition to the normal Python ones.
"""
from __future__ import annotations
from functools import wraps
from copy import copy
# noinspection PyUnresolvedReferences
from subprocess import CalledProcessError


class ErrorUtils:
	@staticmethod
	def args(*names):
		"""
		Decorator.
		Add a __init__ that calls the superclass and takes any argument in names.
		The __init__ will set: (self.name =value if name is passed else None) for all name in names.
		:param names: A sequence of strs
		"""
		assert not any([s=='info' or s.startswith('__') and s.endswith('__') for s in names])
		@wraps(names)
		def dec(cls):
			def _init(self, *args, **kwargs) -> None:
				kwargs = copy(kwargs)
				# when we call super(), we need to know which class we're on and which should be called next
				# note that self will always be the first class
				thisclass = kwargs.pop('__thisclass') if '__thisclass' in kwargs else self.__class__
				for name in names:
					if name in kwargs:
						setattr(self, name, kwargs.pop(name))
					else:
						setattr(self, name, None)
				nextclass = thisclass.__mro__[1]
				# noinspection PyArgumentList
				super(thisclass, self).__init__(*args, __thisclass=nextclass, **kwargs)
			cls.__init__ = _init
			return cls
		return dec

class DscienceBaseException(Exception):
	def __init__(self, *args, **kwargs):
		super().__init__(*args)

	def __eq__(self, other: DscienceBaseException) -> bool:
		return (
				type(self) == type(other)
				and str(self) == str(other)
				and all([getattr(self, name) == getattr(other, name) for name in self.__dict__])
		)

	def info(self) -> str:
		return (
				self.__class__.__name__
				+ ':' + str(self)
				+ '(' + ','.join([
					k + '=' + str(v)
					for k, v in self.__dict__.items()
				]) + ')'
		)

class NaturalException(DscienceBaseException): """Non-specific exception to short-circuit behavior but meaning 'all ok'."""
NaturalExpectedException = NaturalException

class Error(DscienceBaseException):
	"""
	General exception super-type that indicates something is wrong but could potentially be recovered from.
	Equivalent to Python's recommendation to suffix a class name with 'Error'.
	"""
class ImpossibleStateError(Error, AssertionError): """An assertion failed marking invalid state, potentially recoverable."""
class UnsupportedOperationError(Error): """Used as a replacement for NotImplementedError, where the method SHOULD NOT be implemented."""

@ErrorUtils.args('n')
class MultipleMatchesError(Error): """"Multiple records match; has argument `n` containing the number matched as an int"""

class UserError(Error): """A bad command, etc, from a user (not a programmer)"""
@ErrorUtils.args('cmd')
class BadCommandError(UserError): """The user passed an invalid command, such as at the command-line."""
class ConfigError(UserError): pass
class RefusingRequestError(UserError): """The user requested an operation that is understood but is being refused (i.e., because it is dangerous in this context)."""

@ErrorUtils.args('key')
class ResourceError(Error): """A problem finding or loading a resource (file, network connection, hardware, etc.)"""
class LockedError(ResourceError): """A resource was found but is locked (ex a hardware component in use)"""
class MissingEnvironmentVariableError(ResourceError): pass
@ErrorUtils.args('expected', 'actual')
class HashValidationFailedError(ResourceError): """The hash of a resource did not validate"""
class IncompatibleDataError(ResourceError): """An operation cannot be applied to data that has this property. For example, an old generation of the data."""
class MissingResourceError(ResourceError): """Could not find a resource (general case)"""
class LookupFailedError(MissingResourceError): """Could not find a resource by name (typically by the user requesting a resource of that name)"""

class _ArgumentLikeError(Error): """A generic error related to arguments"""
class AmbiguousRequestError(_ArgumentLikeError): pass
class ContradictoryArgumentsError(_ArgumentLikeError): pass
@ErrorUtils.args('key')
class ReservedNameError(_ArgumentLikeError): pass
@ErrorUtils.args('key')
class AlreadyUsedError(_ArgumentLikeError): pass

class _SizeLikeError(Error): pass
@ErrorUtils.args('length', 'minimum', 'maximum')
class LengthError(_SizeLikeError): pass
@ErrorUtils.args('lengths')
class LengthMismatchError(_SizeLikeError): pass
@ErrorUtils.args('actual', 'expected')
class WrongDimensionError(_SizeLikeError): pass
class EmptyCollectionError(_SizeLikeError): pass

@ErrorUtils.args('value')
class _ValueLikeError(Error, ValueError): pass
@ErrorUtils.args('pattern')
class StringPatternError(_ValueLikeError): """A string did not match a required regular expression"""
@ErrorUtils.args('minimum', 'maximum')
class OutOfRangeError(_ValueLikeError): """A numerical value is outside a required range"""
class ZeroDistanceError(_ValueLikeError): """Two (or more) values are the same by distance"""
class NullValueError(_ValueLikeError): """The value None was given"""

@ErrorUtils.args('value')
class _NumericLikeError(Error): pass
class NumericConversionError(_NumericLikeError): pass
class RoundingError(_NumericLikeError): pass

@ErrorUtils.args('key')
class _LookupLikeError(Error, LookupError): pass
class MissingColumnError(_LookupLikeError): pass

# parsing files or similar resources
@ErrorUtils.args('key')
class _ParsingLikeError(Error): pass
class ParsingError(Error): pass
class UnrecognizedKeyError(_ParsingLikeError): """A configuration entry was set, but the code doesn't recognize that name."""

class _WrapLikeError(Error): pass
class DataIntegrityError(_WrapLikeError): """Data (e.g., from a database) is missing, incomplete, or invalid. More complex than a missing value."""
class AlgorithmFailedError(_WrapLikeError): """A wrapper for some less meaningful error."""

class _IoLikeError(Error, IOError): pass
@ErrorUtils.args('device')
class HardwareError(_IoLikeError): pass
class MissingDeviceError(HardwareError): pass
@ErrorUtils.args('key', 'value')
class BadWriteValueError(HardwareError): pass
@ErrorUtils.args('path')
class PathError(_IoLikeError): pass
class InvalidFileError(PathError): pass
class InvalidDirectoryError(PathError): pass
