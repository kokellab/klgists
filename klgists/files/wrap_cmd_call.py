from typing import List
import logging
import subprocess
from klgists.common.exceptions import ExternalCommandFailed


def wrap_cmd_call(cmd: List[str], stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> (str, str):
	"""Calls an external command, waits, and throws a ExternalCommandFailed for nonzero exit codes.
	Returns (stdout, stderr).
	"""
	logging.info("Calling '{}'".format(' '.join(cmd)))
	p = subprocess.Popen(cmd, stdout=stdout, stderr=stderr)
	(out, err) = p.communicate()
	exit_code = p.wait()
	if exit_code != 0:
		logging.error("Standard output\n" + out.decode('utf-8') + "\n\n")
		logging.error("Standard error\n" + err.decode('utf-8') + "\n\n")
		raise ExternalCommandFailed("Got nonzero exit code {} from '{}'".format(exit_code, ' '.join(cmd)))
	return out.decode('utf8'), err.decode('utf8')
