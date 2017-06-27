import re
from typing import Dict

def replace_in_file(path: str, changes: Dict[str, str]) -> None:
	"""Uses re.sub repeatedly to modify (AND REPLACE) a file's content."""
	with open(path) as f: data = f.read()
	for key, value in changes.items():
		data = re.sub(key, value, data, re.MULTILINE, re.DOTALL)
	with open(path, 'w') as f: f.write(data)
