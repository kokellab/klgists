import warnings
import re
from typing import Optional
from klgists.files.wrap_cmd_call import wrap_cmd_call

def find_matlab_version(matlab_path: str) -> Optional[str]:
	"""Calls MATLAB to get its version.
	Note: This takes ~30 seconds.
	"""
	out, err = wrap_cmd_call([
		matlab_path, '-nodesktop', '-nosplash', '-nodisplay', '-r', 'quit'
	])
	m = re.compile('R[0-9]{4}[A-Za-z]*[^\\s]*').search(out)
	if m is not None:
		return m.group(0)
	else:
		warnings.warn('MATLAB responded with output that does not appear to contain version information')
		return None
