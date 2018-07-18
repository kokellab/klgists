import logging
import subprocess
from typing import List, Optional

from klgists import logger
from klgists.common.exceptions import ExternalCommandFailed

def _disp(out, ell, name):
	out = out.strip()
	if '\n' in out:
		ell(name + ":\n<<=====\n" + out + '\n=====>>')
	elif len(out) > 0:
		ell(name + ": <<===== " + out + " =====>>")
	else:
		ell(name + ": <no output>")
	

def _log(out, err, ell):
	_disp(out, ell, "stdout")
	_disp(err, ell, "stderr")


def wrap_cmd_call(cmd: List[str], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell_cmd: str=None, cwd: Optional[str] = None, timeout_secs: Optional[float] = None) -> (str, str):
	"""Calls an external command, waits, and throws a ExternalCommandFailed for nonzero exit codes.
	Returns (stdout, stderr).
	The user can optionally provide a shell to run the command with, e.g. "powershell.exe" 
	"""
	cmd = [str(p) for p in cmd]
	if shell_cmd:
		cmd = [shell_cmd] + cmd
	logger.debug("Calling '{}'".format(' '.join(cmd)))
	p = subprocess.Popen(cmd, stdout=stdout, stderr=stderr, cwd=cwd)
	try:
		(out, err) = p.communicate(timeout=timeout_secs)
	finally:
		p.kill()
	try:
		out = out.decode('utf-8')
		err = err.decode('utf-8')
		exit_code = p.wait(timeout=timeout_secs)
	except:
		_log(out, err, logger.warning)
		raise
	finally:
		p.kill()
	if exit_code != 0:
		_log(out, err, logger.warning)
		raise ExternalCommandFailed("Got nonzero exit code {} from '{}'".format(exit_code, ' '.join(cmd)))
	_log(out, err, logger.debug)
	return out, err
