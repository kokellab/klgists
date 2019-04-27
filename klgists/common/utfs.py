"""
Needed for fully comptabile reading.
"""

from enum import Enum

class Utf(Enum):
	UTF8 = 1
	UTF16 = 2
	UTF32 = 3


__all__ = ['Utf']
