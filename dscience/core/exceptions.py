"""
The motivation here is simply that Python lacks some standard exceptions that I consider important.
Projects can/should subclass from these in addition to the normal Python ones.
"""
from functools import wraps
from copy import copy
from subprocess import CalledProcessError

def _args(*names):
	@wraps(names)
	def dec(cls):
		def _init(self, *args, **kwargs):
			kwargs = copy(kwargs)
			for name in names:
				if name in kwargs:
					setattr(self, name, kwargs.pop(name))
			super(self, *args, **kwargs)
		cls.__init__ = _init
		return cls
	return dec


class NaturalExpectedException(Exception): pass
NaturalException = NaturalExpectedException

class Error(Exception):
	def __init__(self, *args, **kwargs):
		super(Error, self).__init__(*args)
class ImpossibleStateError(Error, AssertionError): pass
class UnsupportedOperationError(Error): """Used as a replacement for NotImplementedError, where the method SHOULD NOT be implemented."""

@_args('n')
class MultipleMatchesError(Error): pass

class UserError(Error): """A bad command, etc, from a user (not a programmer)"""
@_args('cmd')
class BadCommandError(UserError): pass
class ConfigError(UserError): pass
class RefusingRequestError(UserError): pass

@_args('key')
class ResourceError(Error): pass
class LockedError(ResourceError): pass
class MissingEnvironmentVariableError(ResourceError): pass
@_args('expected', 'actual')
class HashValidationFailedError(ResourceError): pass
class IncompatibleDataError(ResourceError): """An operation cannot be applied to data that has this property. For example, an old generation of the data."""
class MissingResourceError(ResourceError): pass
class LookupFailedError(MissingResourceError): pass

class _ArgumentLikeError(Error): pass
class AmbiguousRequestError(_ArgumentLikeError): pass
class ContradictoryArgumentsError(_ArgumentLikeError): pass
@_args('key')
class ReservedNameError(_ArgumentLikeError): pass
@_args('key')
class AlreadyUsedError(_ArgumentLikeError): pass

class _SizeLikeError(Error): pass
@_args('length', 'minimum', 'maximum')
class LengthError(_SizeLikeError): pass
@_args('lengths')
class LengthMismatchError(_SizeLikeError): pass
@_args('actual', 'expected')
class WrongDimensionError(_SizeLikeError): pass
class EmptyCollectionError(_SizeLikeError): pass

@_args('value')
class _ValueLikeError(Error, ValueError): pass
@_args('pattern')
class StringPatternError(_ValueLikeError): pass
@_args('minimum', 'maximum')
class OutOfRangeError(_ValueLikeError): pass
class ZeroDistanceError(_ValueLikeError): pass
class NullValueError(_ValueLikeError): pass

@_args('value')
class _NumericLikeError(Error): pass
class NumericConversionError(_NumericLikeError): pass
class RoundingError(_NumericLikeError): pass

@_args('key')
class _LookupLikeError(Error, LookupError): pass
class MissingColumnError(_LookupLikeError): pass

# parsing files or similar resources
@_args('key')
class _ParsingLikeError(Error): pass
class ParsingError(Error): pass
class UnrecognizedKeyError(_ParsingLikeError): """A configuration entry was set, but the code doesn't recognize that name."""

class _WrapLikeError(Error): pass
class DataIntegrityError(_WrapLikeError): """Data (e.g., from a database) is missing, incomplete, or invalid. More complex than a missing value."""
class AlgorithmFailedError(_WrapLikeError): """A wrapper for some less meaningful error."""

class _IoLikeError(Error, IOError): pass
@_args('device')
class HardwareError(_IoLikeError): pass
class MissingDeviceError(HardwareError): pass
@_args('key', 'value')
class BadWriteValueError(HardwareError): pass
@_args('path')
class PathError(_IoLikeError): pass
class InvalidFileError(PathError): pass
class InvalidDirectoryError(PathError): pass
