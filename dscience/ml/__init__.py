from dscience.core import SmartEnum

class ErrorBehavior(SmartEnum):
	FAIL = 1
	LOG_ERROR = 2
	LOG_WARNING = 3
	LOG_CAUTION = 4
	IGNORE = 5

__all__ = ['ErrorBehavior']
