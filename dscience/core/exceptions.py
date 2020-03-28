"""
The motivation here is simply that Python lacks some standard exceptions that I consider important.
Projects can/should subclass from these in addition to the normal Python ones.
"""
from __future__ import annotations
from typing import Collection, Any, Union
import os
from pathlib import Path
from functools import wraps
from copy import copy
# noinspection PyUnresolvedReferences
from subprocess import CalledProcessError
import logging
logger = logging.getLogger('dscience')
KeyLike = Any
PathLike = Union[Path, str, os.PathLike]
_DW = DeprecationWarning
_PDW = PendingDeprecationWarning

class ErrorUtils:
	"""Utilities for creating and modifying errors."""
	@staticmethod
	def args(**names):
		"""
		Decorator.
		Add a __init__ that calls the superclass and takes any argument in names.
		The __init__ will set: (self.name =value if name is passed else None) for all name in names.
		:param names: A map from str to Type
		"""
		assert not any([s=='info' or s.startswith('__') and s.endswith('__') for s in names])
		@wraps(names)
		def dec(cls):
			def _doc(doc: str) -> str:
				return doc + '\n' + 'Supports attributes:\n' + '\n'.join([
					'    • ' + name + ': ' + str(dtype)
					for name, dtype in names.items()
				])
			def _init(self, *args, **kwargs) -> None:
				kwargs = copy(kwargs)
				# when we call super(), we need to know which class we're on and which should be called next
				# note that self will always be the first class
				thisclass = kwargs.pop('__thisclass') if '__thisclass' in kwargs else self.__class__
				for name, reqtype in names.items():
					if name in kwargs:
						value = kwargs.pop(name)
						# TODO in the future, we can warn when type-checks fail; impossible in current Python
						setattr(self, name, value)
					else:
						setattr(self, name, None)
					nextclass = thisclass.__mro__[1]
					# noinspection PyArgumentList
					super(thisclass, self).__init__(*args, __thisclass=nextclass, **kwargs)
			cls.__init__ = _init
			cls.__doc__ = _doc(cls.__doc__)
			return cls
		return dec


class _FnUtils:
	"""
	Abstract class for warnings and errors that can contain extra attributes.
	"""

	def eq(self, other) -> bool:
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
					for k, v in sorted(self.__dict__.items())
				]) + ')'
		)

# NOTE: line 2nd col at 50 chars, no matter what
# This indendation makes it easy to see new definitions
# If not possible, adjust only for that line
# Don't adjust existing lines from 50 to avoid git tracking

class XException(Exception):
	"""Abstract exception whose subclasses can define extra attributes using ErrorTools.args."""
	def __init__(self, *args, **kwargs): pass
	info = _FnUtils.info
	__eq__ = _FnUtils.eq

class XWarning(UserWarning):
	"""Abstract user warning whose subclasses can define extra attributes using ErrorTools.args."""
	def __init__(self, *args, **kwargs): pass
	info = _FnUtils.info
	__eq__ = _FnUtils.eq

class Error(XException):                         """Abstract exception could reasonably be recovered from. Subclass names should end with 'Error'."""
class NaturalExpectedError(Error):               """Non-specific exception to short-circuit behavior but meaning 'all ok'."""

class _CodeWarning(XWarning):                    """A warning related to code quality."""
class ObsoleteWarning(_CodeWarning, _PDW):       """The code being called is obsolete and/or may be deprecated in the future."""
class DeprecatedWarning(_CodeWarning, _DW):      """The code being called is deprecated."""
class ImmatureWarning(_CodeWarning):             """The code being called is unstable or immature."""

class _OpWarning(XWarning):                      """A warning related to problematic requests."""
class DangerousRequestWarning(_OpWarning):       """A warning about an operation that is dangerous but is proceeding regardless."""
class StrangeRequestWarning(_OpWarning):         """A warning about a potential result being wrong because weird arguments were passed."""
class IgnoringRequestWarning(_OpWarning):        """A request or passed argument was ignored."""

class _MissingWarning(XWarning):                 """A request related to something missing."""
@ErrorUtils.args(package=str)
class ImportFailedWarning(_MissingWarning):      """Could not import a recommended package."""
@ErrorUtils.args(key=KeyLike)
class ConfigWarning(_MissingWarning):            """Did not find a recommended config entry, etc."""

class AlgorithmWarning(XWarning):                """A warning about a potential result being wrong."""

@ErrorUtils.args(data_key=KeyLike)
class DataWarning(XWarning):                     """External data is suspicious / might contain an error."""

class IllegalStateError(Error, AssertionError):  """An assertion failed marking invalid state, potentially recoverable."""

class UnsupportedOpError(Error):                 """Used as a replacement for NotImplementedError, where the method SHOULD NOT be implemented."""
@ErrorUtils.args(class_name=str)
class ImmutableError(UnsupportedOpError):        """Tried to mutate an immutable object."""
class OpStateError(UnsupportedOpError):          """The operation cannot be performed on an object in this state."""

@ErrorUtils.args(n=int)
class MultipleMatchesError(Error):               """Multiple records match; has argument `n` containing the number matched as an int"""

class UserError(Error):                          """A bad command, etc, from a user (not a programmer)"""
@ErrorUtils.args(cmd=str)
class BadCommandError(UserError):                """The user passed an invalid command, such as at the command-line."""
class ConfigError(UserError):                    """Error while interpreting a config file from the user."""
class MissingConfigKeyError(UserError):          """Missing a required key."""
class RefusingRequestError(UserError):           """The user requested an operation that is understood but is being refused."""

@ErrorUtils.args(key=KeyLike)
class ResourceError(Error):                      """A problem finding or loading a resource (file, network connection, hardware, etc.)"""
class LockedError(ResourceError):                """A resource was found but is locked (ex a hardware component in use)"""
class MissingEnvVarError(ResourceError):         """Missing a required environment variable"""
@ErrorUtils.args(expected=str, actual=str)
class HashValidationFailedError(ResourceError):  """The hash of a resource did not validate"""
class IncompatibleDataError(ResourceError):      """An operation cannot be applied to data with this property value."""
class MismatchedDataError(ResourceError):             """A property of the data is different between multiple elements."""
class MissingResourceError(ResourceError):       """Could not find a resource (general case)"""
class LookupFailedError(MissingResourceError):   """Could not find a resource by name."""

class _ReqError(Error):                          """A generic error related to arguments"""
class AmbiguousRequestError(_ReqError):          """Insufficient information was passed to resolve the operation"""
class ContradictoryRequestError(_ReqError):      """Contradictory information was passed"""
@ErrorUtils.args(key=KeyLike)
class ReservedError(_ReqError):                  """A key is reserved by the code and cannot be used"""
@ErrorUtils.args(key=KeyLike)
class AlreadyUsedError(_ReqError):               """A key was specified twice"""

class _SizeError(Error):                         """Too small or large for the operation"""
@ErrorUtils.args(length=int, minimum=int, maximum=int)
class LengthError(_SizeError):                   """The length is too large or too small"""
@ErrorUtils.args(lengths=Collection[int])
class LengthMismatchError(_SizeError):           """The objects (1 or more) have different lengths"""
@ErrorUtils.args(expected=int, actual=int)
class WrongDimensionError(_SizeError):           """The object has the wrong number of dimensions (ex matrix instead of vector)"""
class EmptyCollectionError(_SizeError):          """The object has no elements"""

@ErrorUtils.args(expected=str, actual=str)
class XTypeError(Error, TypeError):              """A TypeError containing the expected and actual types"""

@ErrorUtils.args(value=KeyLike)
class XValueError(Error, ValueError):            """A ValueError containing the value"""
@ErrorUtils.args(pattern=str)
class StringPatternError(XValueError):           """A string did not match a required regular expression"""
@ErrorUtils.args(minimum=int, maximum=int)
class OutOfRangeError(XValueError):              """A numerical value is outside a required range"""
class ZeroDistanceError(XValueError):            """Two (or more) values are the same by distance"""
class NullValueError(XValueError):               """A value of None, NaN, or similar was given"""

@ErrorUtils.args(value=KeyLike)
class _NumericError(Error):                      """An error with a (simple) numeric operation."""
class NumericConversionError(_NumericError):     """Could not convert one numeric type to another"""
class InexactRoundError(_NumericError):          """A floating-point number could not be cast to an integer"""

@ErrorUtils.args(key=KeyLike)
class _KeyError(Error, KeyError):                """KeyError that contains the failed key"""
class MissingColumnError(_KeyError):             """Missing column in a DataFrame"""

# parsing files or similar resources
@ErrorUtils.args(resource=Any)
class _ParsingLikeError(Error):                  """Failed to parse"""
class ParsingError(Error):                       """Syntax error when parsing"""
@ErrorUtils.args(item=KeyLike)
class UnrecognizedKeyError(_ParsingLikeError):   """A configuration entry was set, but the code doesn't recognize that name."""

class _WrapLikeError(Error): pass
class DataIntegrityError(_WrapLikeError):        """Data is missing, incomplete, or invalid. More complex than a missing value."""
class AlgorithmError(_WrapLikeError):            """A wrapper for some less meaningful error."""
class ConstructionError(_WrapLikeError):         """A wrapper for some less meaningful error."""

class _IoError(Error, IOError):                  """Error related to the filesystem or I/O."""
@ErrorUtils.args(device=KeyLike)
class HardwareError(_IoError):                   """Error related to hardware such as an Arduino."""
class DeviceConnectionError(HardwareError):      """"Could not connect to the device."""
class MissingDeviceError(HardwareError):         """"Could not find the needed device."""
@ErrorUtils.args(key=KeyLike, value=Any)
class BadWriteError(HardwareError):              """Could not write to a hardware device (typically to a pin)."""

@ErrorUtils.args(key=KeyLike)
class _LoadSaveError(_IoError):                  """Error loading or saving a file."""
class LoadError(_LoadSaveError):                 """Failed to load a file."""
class SaveError(_LoadSaveError):                 """Failed to save a file."""
class CacheLoadError(_LoadSaveError):            """Failed to load a file from a cache."""
class CacheSaveError(_LoadSaveError):            """Failed to save a file to a cache."""
class DownloadError(_LoadSaveError):             """Failed to download a file."""
class UploadError(_LoadSaveError):               """Failed to upload a file."""


@ErrorUtils.args(path=PathLike)
class PathError(_IoError):                       """Error involving a path on the filesystem."""
class FileDoesNotExistError(PathError):          """The path is not a valid file."""
class DirDoesNotExistError(PathError):           """The path is not a valid directory."""
class IllegalPathError(PathError):               """Not a valid path."""
class PathExistsError(PathError):                """The path already exists."""
