import logging
import subprocess
from typing import List, Optional

from klgists.common.exceptions import ExternalCommandFailed


def wrap_cmd_call(cmd: List[str], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell_cmd: str=None, timeout_secs: Optional[float] = None) -> (str, str):
	"""Calls an external command, waits, and throws a ExternalCommandFailed for nonzero exit codes.
	Returns (stdout, stderr).
	The user can optionally provide a shell to run the command with, e.g. "powershell.exe" 
	"""
	cmd = [str(p) for p in cmd]
	if shell_cmd:
		cmd = [shell_cmd] + cmd
	logging.info("Calling '{}'".format(' '.join(cmd)))
	p = subprocess.Popen(cmd, stdout=stdout, stderr=stderr, cwd=cwd)
	(out, err) = p.communicate()
	exit_code = p.wait(timeout=timeout_secs)
	if exit_code != 0:
		logging.error("Standard output\n" + out.decode('utf-8') + "\n\n")
		logging.error("Standard error\n" + err.decode('utf-8') + "\n\n")
		raise ExternalCommandFailed("Got nonzero exit code {} from '{}'".format(exit_code, ' '.join(cmd)))
	return out.decode('utf8'), err.decode('utf8')
