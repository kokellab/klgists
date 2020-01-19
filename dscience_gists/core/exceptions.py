"""
The motivation here is simply that Python lacks some standard exceptions that I consider important.
Projects can/should subclass from these in addition to the normal Python ones.
"""
from enum import Enum

class LengthMismatchError(IndexError): pass
class OutOfRangeError(IndexError): pass
class NaturalExpectedException(Exception): pass
class MultipleMatchesException(Exception): pass
class HashValidationFailedError(Exception): pass
class ImpossibleStateError(AssertionError): pass

class UserError(Exception): pass
class BadCommandError(UserError): pass
class LookupFailedError(UserError): pass
class BadConfigError(UserError): pass
class ParsingError(UserError): pass

class RefusingRequestError(UserError): pass
class LockedError(RefusingRequestError): pass
class MissingResourceException(UserError): pass
class MissingEnvironmentVariableError(UserError, KeyError): pass
class ParsingFailedError(UserError): pass

class MissingDeviceError(UserError): pass
class BadWriteValueError(MissingDeviceError): pass

class PathError(IOError): pass
class InvalidFileError(PathError): pass
class InvalidDirectoryError(PathError): pass

class ExternalCommandFailed(IOError):
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

