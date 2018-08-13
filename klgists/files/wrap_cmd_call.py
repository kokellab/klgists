import logging
import subprocess
from enumeration import Enum
from subprocess import Popen, PIPE
from queue import Queue
from threading import Thread
from typing import List, Optional, Callable

from klgists import logger
from klgists.common.exceptions import ExternalCommandFailed

class PipeType(Enum):
	STDOUT = 1
	STDERR = 2

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

	
def smart_log_callback(source, line, prefix: str = '') -> None:
	line = line.decode('utf-8')
	if line.startswith('FATAL:'):
		logger.fatal(prefix + line)
	elif line.startswith('ERROR:'):
		logger.error(prefix + line)
	elif line.startswith('WARNING:'):
		logger.warning(prefix + line)
	elif line.startswith('INFO:'):
		logger.info(prefix + line)
	elif line.startswith('DEBUG:'):
		logger.debug(prefix + line)
	else:
		logger.debug(prefix + line)
	
	
def stream_cmd_call(cmd: List[str], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell_cmd: str=None, cwd: Optional[str] = None, timeout_secs: Optional[float] = None, log_callback: Callable[[PipeType, bytes], None] = None, bufsize: int = 1) -> None:
	"""Calls an external command, waits, and throws a ExternalCommandFailed for nonzero exit codes.
	Returns (stdout, stderr).
	The user can optionally provide a shell to run the command with, e.g. "powershell.exe" 
	"""
	if log_callback is None:
		log_callback = smart_log_callback
	cmd = [str(p) for p in cmd]
	if shell_cmd:
		cmd = [shell_cmd] + cmd
	logger.debug("Calling '{}'".format(' '.join(cmd)))
	p = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, cwd=cwd, bufsize=bufsize)
	try:
		q = Queue()
		Thread(target=reader, args=[PipeType.STDOUT, q]).start()
		Thread(target=reader, args=[PipeType.STDERR, q]).start()
		for _ in range(2):
			for source, line in iter(q.get, None):
				log_callback(source, line)
		exit_code = p.wait(timeout=timeout_secs)
	finally:
		p.kill()
	if exit_code != 0:
		raise ExternalCommandFailed("Got nonzero exit code {} from '{}'".format(exit_code, ' '.join(cmd)))
	return out, err
	

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
	out, err, exit_code = None, None, None
	try:
		(out, err) = p.communicate(timeout=timeout_secs)
		out = out.decode('utf-8')
		err = err.decode('utf-8')
		exit_code = p.wait(timeout=timeout_secs)
	except Exception as e:
		_log(out, err, logger.warning)
		raise e
	finally:
		p.kill()
	if exit_code != 0:
		_log(out, err, logger.warning)
		raise ExternalCommandFailed("Got nonzero exit code {} from '{}'".format(exit_code, ' '.join(cmd)))
	_log(out, err, logger.debug)
	return out, err
