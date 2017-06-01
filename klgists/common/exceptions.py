
class ExternalDeviceNotFound(IOError): pass

class TimeoutException(IOError): pass

class ExternalCommandFailed(Exception):
	message = None  # type: str
	def __init__(self, message: str) -> None:
		self.message = message

class MissingComponentException(Exception):
	message = None
	def __init__(self, message: str):
		self.message = message

class BadCommandError(Exception):
	message = None
	def __init__(self, message: str):
		self.message = message

class BadConfigException(Exception):
	message = None  # type: str
	def __init__(self, message: str) -> None:
		self.message = message
