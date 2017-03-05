
class ExternalDeviceNotFound(IOError): pass

class TimeoutException(IOError): pass

class MissingComponentException(Exception):
	message = None
	def __init__(self, message: str):
		self.message = message

class BadCommandError(Exception):
	message = None
	def __init__(self, message: str):
		self.message = message
