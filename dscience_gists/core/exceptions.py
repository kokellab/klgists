"""
The motivation here is simply that Python lacks some standard exceptions that I consider important.
Projects can/should subclass from these in addition to the normal Python ones.
"""

class NaturalExpectedException(Exception): pass
class Error(Exception): pass

class LengthMismatchError(Error): pass
class OutOfRangeError(Error, IndexError): pass
class HashValidationFailedError(Error): pass
class ImpossibleStateError(Error, AssertionError): pass

class AmbiguousRequestError(Error): pass
class ContradictoryArgumentsError(Error): pass
class ReservedNameError(Error): pass
class AlreadyUsedError(Error): pass

class EmptyCollectionError(Error): pass
class ZeroDistanceError(Error): pass
class NullValueError(Error): pass
class TooFewError(Error): pass
class MultipleMatchesError(Exception): pass
class UnsupportedOperationError(Error): """Used as a replacement for NotImplementedError, where the method SHOULD NOT be implemented."""
class IncompatibleDataError(Error): """An operation cannot be applied to data that has this property. For example, an old generation of the data."""

class MissingColumnError(Error): pass
class UserError(Error): pass
class BadCommandError(UserError): pass
class LookupFailedError(UserError): pass
class BadConfigError(UserError): pass
class ParsingError(UserError): pass

class DataIntegrityError(Error):
	"""Data (e.g., from a database) is missing, incomplete, or invalid. More complex than a missing value."""
class AlgorithmFailedError(Error):
	"""A wrapper for some less meaningful error."""
class NumericConversionError(Error): pass
class RoundingError(NumericConversionError): pass
class RefusingRequestError(UserError): pass
class LockedError(RefusingRequestError): pass
class MissingResourceError(UserError): pass
class MissingEnvironmentVariableError(UserError, KeyError): pass
class UnrecognizedConfigKeyError(BadConfigError): """A configuration entry was set, but the code doesn't recognize that name."""


class MissingDeviceError(UserError): pass
class BadWriteValueError(MissingDeviceError): pass

class PathError(Error, IOError): pass
class InvalidFileError(PathError): pass
class InvalidDirectoryError(PathError): pass

class ExternalCommandError(Error, IOError):
	"""
	Deprecated.
	"""
	def __init__(self, message, command: str, exit_code: int, stdout: str, stderr: str):
		super().__init__(message)
		self.command = command
		self.exit_code = exit_code
		self.stdout = stdout
		self.stderr = stderr
	def extended_message(self) -> str:
		return "Command `{}` failed with exit code `{}`.\nstdout:{}\nstderr:{}"\
			.format(self.command, self.exit_code, self._x(self.stdout), self._x(self.stderr))
	def _x(self, out):
		out = out.strip()
		if '\n' in out:
			return "\n<<=====\n" + out + '\n=====>>'
		elif len(out) > 0:
			return " <<===== " + out + " =====>>"
		else:
			return " <no output>"

