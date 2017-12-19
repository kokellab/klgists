"""
The motivation here is simply that Python lacks some standard exceptions that I consider important.
Projects can/should subclass from these in addition to the normal Python ones.
"""


class NaturalExpectedException(Exception): pass

class HelpRequestedException(NaturalExpectedException): pass


class PreconditionFailedException(Exception): pass

class MultipleMatchesException(Exception): pass

class HashValidationFailedException(Exception): pass


# hardware and OS errors

class ExternalDeviceNotFound(IOError): pass

class TimeoutException(IOError): pass  # maybe just Python's timeout error?

class ExternalCommandFailed(IOError): pass

class MissingComponentException(IOError): pass

class InsufficientResourceException(OSError): pass


# user errors

class UserError(Exception): pass

class BadCommandError(UserError): pass

class BadConfigException(UserError): pass  # this one's a bit ambiguous

class UserContradictionException(UserError): pass

class RefusingRequestException(UserError): pass

class ParsingFailedException(UserError): pass


# path errors

class PathException(IOError): pass

class NoSuchPathException(PathException, FileNotFoundError): pass

class NoSuchFileException(NoSuchPathException): pass

class NoSuchDirectoryException(NoSuchPathException): pass

class PathAlreadyExistsException(PathException): pass

class PathIsNotFileException(PathAlreadyExistsException): pass

class PathIsNotDirectoryException(PathAlreadyExistsException): pass
