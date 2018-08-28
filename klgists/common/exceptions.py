"""
The motivation here is simply that Python lacks some standard exceptions that I consider important.
Projects can/should subclass from these in addition to the normal Python ones.
"""

from enum import Enum


class NaturalExpectedException(Exception): pass

class HelpRequestedException(NaturalExpectedException): pass


class PreconditionFailedException(Exception): pass

class MultipleMatchesException(Exception): pass

class HashValidationFailedException(Exception): pass


class ImpossibleStateException(AssertionError):
	"""Refers explicitly to state."""
	pass


# hardware and OS errors

class ExternalDeviceNotFound(IOError): pass

class TimeoutException(IOError): pass

class ExternalCommandFailed(IOError):
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

class MissingComponentException(IOError): pass

class InsufficientResourceException(OSError): pass


# user errors

class UserError(Exception): pass

class MissingConfigEntry(UserError): pass

class BadCommandError(UserError): pass

class LookupFailedException(UserError): pass

class BadConfigException(UserError): pass

class Edge(Enum):
	LEFT = 1
	RIGHT = 2
	TOP = 3
	BOTTOM = 4

class Axis(Enum):
	HORIZONTAL = 1
	VERTICAL = 2

class RoiError(BadConfigException):
	def __init__(self, message, errors = None, edge: Edge = None, axis: Axis = None):
		super().__init__(message, errors)
		self.edge = None
		self.axis = None
	def on_edge(self, edge: Edge): self.edge = edge; return self
	def on_axis(self, axis: Axis): self.axis = axis; return self


class RoiOutOfBoundsError(RoiError): pass
class NegativeRoiBoundsError(RoiError): pass
class FlippedRoiBoundsError(RoiError): pass

class UserContradictionException(UserError): pass

class RefusingRequestException(UserError): pass

class LockedException(RefusingRequestException): pass

class MissingResourceException(UserError): pass

class MissingEnvironmentVariableException(UserError, KeyError): pass

class ParsingFailedException(UserError): pass


# EE-related user errors

class BoardUserError(UserError): pass

class BadPinWriteValueException(BoardUserError): pass

class NoSuchInputPinException(BoardUserError): pass

class NoSuchOutputPinException(BoardUserError): pass


# path errors

class PathException(IOError): pass

class NoSuchPathException(PathException, FileNotFoundError): pass

class NoSuchFileException(NoSuchPathException): pass

class NoSuchDirectoryException(NoSuchPathException): pass

class PathAlreadyExistsException(PathException): pass

class PathIsNotFileException(PathAlreadyExistsException): pass

class PathIsNotDirectoryException(PathAlreadyExistsException, NotADirectoryError): pass
