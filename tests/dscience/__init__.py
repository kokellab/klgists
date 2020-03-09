import os

def load(parts):
	if isinstance(parts, str): parts = [parts]
	return os.path.join(os.path.dirname(__file__), '..', 'resources', 'common', *parts)

